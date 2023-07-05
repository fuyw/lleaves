import os
from pathlib import Path

import llvmlite.binding as llvm


def _initialize_llvm():
    # this initializes the per-process LLVM state. It's save to call multiple times.
    # TODO we never call llvm.shutdown(), is this a problem?
    # some parts of the llvm memory are only deallocated once the process exits
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()


def _get_target_machine(fcodemodel="large"):
    target = llvm.Target.from_triple(llvm.get_process_triple())
    # try:
    #     # LLVM raises if features cannot be detected
    #     features = llvm.get_host_cpu_features().flatten()
    # except RuntimeError:
    #     features = ""
    features = '+64bit,+adx,+aes,-amx-bf16,-amx-int8,-amx-tile,+avx,+avx2,-avx512bf16,-avx512bitalg,-avx512bw,-avx512cd,-avx512dq,-avx512er,-avx512f,-avx512ifma,-avx512pf,-avx512vbmi,-avx512vbmi2,-avx512vl,-avx512vnni,-avx512vp2intersect,-avx512vpopcntdq,+bmi,+bmi2,-cldemote,-clflushopt,-clwb,-clzero,+cmov,+cx16,+cx8,-enqcmd,+f16c,+fma,-fma4,+fsgsbase,+fxsr,-gfni,+invpcid,-lwp,+lzcnt,+mmx,+movbe,-movdir64b,-movdiri,-mwaitx,+pclmul,-pconfig,-pku,+popcnt,-prefetchwt1,+prfchw,-ptwrite,-rdpid,+rdrnd,+rdseed,+rtm,+sahf,-serialize,-sgx,-sha,-shstk,+sse,+sse2,+sse3,+sse4.1,+sse4.2,-sse4a,+ssse3,-tbm,-tsxldtrk,-vaes,-vpclmulqdq,-waitpkg,-wbnoinvd,-xop,+xsave,-xsavec,+xsaveopt,-xsaves'

    # large codemodel is necessary for large, ~1000 tree models.
    # for smaller models "default" codemodel would be faster.
    target_machine = target.create_target_machine(
        cpu=llvm.get_host_cpu_name(),
        features=features,
        reloc="pic",
        codemodel=fcodemodel,
    )
    return target_machine


def compile_module_to_asm(module, cache_path=None, fcodemodel="large"):
    _initialize_llvm()

    # Create a target machine representing the host
    target_machine = _get_target_machine(fcodemodel)

    # Create execution engine for our module
    execution_engine = llvm.create_mcjit_compiler(module, target_machine)
    module.data_layout = str(execution_engine.target_data)

    # when caching we dump the executable once the module finished compiling
    # we only ever have one module, hence we can ignore the 'llvm_module' parameter
    # if the module is already cached we load the bytes without any cache-consistency checks
    if cache_path:
        if Path(cache_path).exists():
            execution_engine.set_object_cache(
                getbuffer_func=lambda _: Path(cache_path).read_bytes()
            )
        else:
            execution_engine.set_object_cache(
                notify_func=lambda _, buffer: Path(cache_path).write_bytes(buffer)
            )

    # compile IR to ASM
    execution_engine.finalize_object()
    execution_engine.run_static_constructors()

    if os.environ.get("LLEAVES_PRINT_ASM") == "1":
        print(target_machine.emit_assembly(module))

    return execution_engine
