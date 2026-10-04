import ast
import math
import operator


class CalculationError(ValueError):
    """Raised when an expression cannot be calculated safely."""


BINARY_OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculate(expression: str, angle_mode: str = "DEG") -> int | float:
    if angle_mode not in {"DEG", "RAD"}:
        raise CalculationError("角度单位必须为 DEG 或 RAD")
    normalized = expression.strip().replace("×", "*").replace("÷", "/").replace("^", "**").replace("π", "pi")
    if not normalized:
        raise CalculationError("表达式不能为空")
    if len(normalized) > 1000:
        raise CalculationError("表达式过长")
    try:
        result = _evaluate(ast.parse(normalized, mode="eval").body, angle_mode)
    except SyntaxError as exc:
        raise CalculationError("表达式格式不正确") from exc
    except ZeroDivisionError as exc:
        raise CalculationError("除数不能为零") from exc
    except OverflowError as exc:
        raise CalculationError("计算结果超出允许范围") from exc
    except RecursionError as exc:
        raise CalculationError("表达式过于复杂") from exc
    if isinstance(result, complex) or not math.isfinite(result) or abs(result) > 1e100:
        raise CalculationError("计算结果超出允许范围")
    return result


def _evaluate(node: ast.AST, angle_mode: str) -> int | float:
    if isinstance(node, ast.Name) and node.id in {"pi", "e"}:
        return {"pi": math.pi, "e": math.e}[node.id]
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if abs(node.value) > 1e100:
                raise CalculationError("数字超出允许范围")
            return node.value
        raise CalculationError("只允许输入数字")
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        base, exponent = _evaluate(node.left, angle_mode), _evaluate(node.right, angle_mode)
        if abs(exponent) > 1000:
            raise CalculationError("指数必须在 -1000 到 1000 之间")
        if base == 0 and exponent < 0:
            raise CalculationError("零不能进行负数次幂运算")
        if base < 0 and exponent != int(exponent):
            raise CalculationError("负数不能进行非整数次幂运算")
        result = math.pow(base, exponent)
        if not math.isfinite(result) or abs(result) > 1e100:
            raise CalculationError("计算结果超出允许范围")
        return result
    if isinstance(node, ast.Call):
        if (isinstance(node.func, ast.Name) and node.func.id in {"sqrt", "log", "ln", "sin", "cos", "tan"}
                and len(node.args) == 1 and not node.keywords):
            value = _evaluate(node.args[0], angle_mode)
            name = node.func.id
            if name == "sqrt":
                if value < 0:
                    raise CalculationError("负数不能开平方根")
                return math.sqrt(value)
            if name in {"log", "ln"}:
                if value <= 0:
                    raise CalculationError("对数的输入必须大于零")
                return math.log10(value) if name == "log" else math.log(value)
            if not math.isfinite(value):
                raise CalculationError("三角函数输入超出允许范围")
            radians = math.radians(value) if angle_mode == "DEG" else value
            if name == "tan" and abs(math.cos(radians)) < 1e-12:
                raise CalculationError("该角度的正切无定义")
            return {"sin": math.sin, "cos": math.cos, "tan": math.tan}[name](radians)
        raise CalculationError("仅支持 sqrt、log、ln、sin、cos、tan 函数")
    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
        return BINARY_OPERATORS[type(node.op)](_evaluate(node.left, angle_mode), _evaluate(node.right, angle_mode))
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
        return UNARY_OPERATORS[type(node.op)](_evaluate(node.operand, angle_mode))
    raise CalculationError("仅支持四则运算、幂、sqrt()、小数和括号")
