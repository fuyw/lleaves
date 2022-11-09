import llvmlite.binding as llvm
import llvmlite.ir

DOUBLE = ir.DoubleType()


def add_version_info(module, fversion_func_name):
    """
    Add version info for the forest for debug.
    """
    fversion_func = ir.Function(
        module,
        ir.FunctionType(DOUBLE, [DOUBLE]),
        name=fversion_func_name,
    )
    fversion_block = fversion_func.append_basic_block("version")
    builder = ir.IRBuilder(fversion_block)
    x, = fveresion_func.args
    result = builder.fadd(x, ir.Constant(double, 0.0))
    builder.ret(result)

