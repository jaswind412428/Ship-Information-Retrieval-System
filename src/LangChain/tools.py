"""LangChain Tools：只放可獨立測試的確定性功能。"""

from math import isfinite

from langchain.tools import tool


@tool
def calculate_froude_number(speed_mps: float, waterline_length_m: float) -> str:
    """計算船舶 Froude number。輸入船速（m/s）與水線長（m）；適用於基本無因次速度判讀。"""

    if not isfinite(speed_mps) or speed_mps < 0:
        return "錯誤：船速必須是大於或等於 0 的有限數值。"
    if not isfinite(waterline_length_m) or waterline_length_m <= 0:
        return "錯誤：水線長必須是大於 0 的有限數值。"

    gravity_mps2 = 9.80665
    froude_number = speed_mps / (gravity_mps2 * waterline_length_m) ** 0.5
    return (
        f"Froude number = {froude_number:.5f}；"
        f"使用 Fn = V / sqrt(g × L)，V={speed_mps} m/s，"
        f"L={waterline_length_m} m，g={gravity_mps2} m/s²。"
    )


DEFAULT_TOOLS = [calculate_froude_number]

