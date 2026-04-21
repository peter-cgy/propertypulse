"""
投资分析计算模块
计算 CAP Rate、现金流、投资回报率等指标
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class InvestmentAnalysis:
    """投资分析结果"""
    cap_rate: float  # 资本化率
    gross_rent_multiplier: float  # 租售比
    monthly_cashflow: float  # 月现金流
    annual_cashflow: float  # 年现金流
    cash_on_cash_return: float  # 现金回报率
    price_per_sqft: float  # 每平方英尺价格
    rent_per_sqft: float  # 每平方英尺租金
    break_even_ratio: float  # 盈亏平衡比率
    investment_grade: str  # 投资评级 (A/B/C/D)


class InvestmentCalculator:
    """投资分析计算器"""

    # 默认参数
    DEFAULT_DOWN_PAYMENT_PERCENT = 0.20  # 首付比例 20%
    DEFAULT_INTEREST_RATE = 0.07  # 贷款利率 7%
    DEFAULT_LOAN_TERM_YEARS = 30  # 贷款期限 30年
    DEFAULT_PROPERTY_TAX_RATE = 0.012  # 房产税率 1.2%
    DEFAULT_INSURANCE_RATE = 0.005  # 保险费率 0.5%
    DEFAULT_MAINTENANCE_RATE = 0.01  # 维护费用率 1%
    DEFAULT_VACANCY_RATE = 0.05  # 空置率 5%
    DEFAULT_MANAGEMENT_FEE_RATE = 0.08  # 物业管理费率 8%

    def __init__(
        self,
        down_payment_percent: float = DEFAULT_DOWN_PAYMENT_PERCENT,
        interest_rate: float = DEFAULT_INTEREST_RATE,
        loan_term_years: int = DEFAULT_LOAN_TERM_YEARS,
        property_tax_rate: float = DEFAULT_PROPERTY_TAX_RATE,
        insurance_rate: float = DEFAULT_INSURANCE_RATE,
        maintenance_rate: float = DEFAULT_MAINTENANCE_RATE,
        vacancy_rate: float = DEFAULT_VACANCY_RATE,
        management_fee_rate: float = DEFAULT_MANAGEMENT_FEE_RATE,
    ):
        self.down_payment_percent = down_payment_percent
        self.interest_rate = interest_rate
        self.loan_term_years = loan_term_years
        self.property_tax_rate = property_tax_rate
        self.insurance_rate = insurance_rate
        self.maintenance_rate = maintenance_rate
        self.vacancy_rate = vacancy_rate
        self.management_fee_rate = management_fee_rate

    def calculate(
        self,
        price: float,
        rent: float,
        square_feet: int = 1000,
    ) -> InvestmentAnalysis:
        """
        计算投资分析指标

        Args:
            price: 房产价格
            rent: 月租金
            square_feet: 面积（平方英尺）

        Returns:
            InvestmentAnalysis 投资分析结果
        """
        if price <= 0 or rent <= 0:
            return InvestmentAnalysis(
                cap_rate=0,
                gross_rent_multiplier=0,
                monthly_cashflow=0,
                annual_cashflow=0,
                cash_on_cash_return=0,
                price_per_sqft=0,
                rent_per_sqft=0,
                break_even_ratio=0,
                investment_grade="N/A"
            )

        # 1. CAP Rate = 年租金 / 房产价格
        annual_rent = rent * 12
        cap_rate = (annual_rent / price) * 100

        # 2. 租售比 = 房产价格 / 年租金
        gross_rent_multiplier = price / annual_rent if annual_rent > 0 else 0

        # 3. 每平方英尺价格和租金
        price_per_sqft = price / square_feet if square_feet > 0 else 0
        rent_per_sqft = rent / square_feet if square_feet > 0 else 0

        # 4. 计算月供
        loan_amount = price * (1 - self.down_payment_percent)
        monthly_rate = self.interest_rate / 12
        num_payments = self.loan_term_years * 12

        if monthly_rate > 0:
            monthly_mortgage = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** num_payments
            ) / ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_mortgage = loan_amount / num_payments

        # 5. 计算各项支出
        monthly_property_tax = (price * self.property_tax_rate) / 12
        monthly_insurance = (price * self.insurance_rate) / 12
        monthly_maintenance = rent * self.maintenance_rate
        monthly_vacancy_loss = rent * self.vacancy_rate
        monthly_management_fee = rent * self.management_fee_rate

        # 6. 总支出
        total_monthly_expenses = (
            monthly_mortgage +
            monthly_property_tax +
            monthly_insurance +
            monthly_maintenance +
            monthly_vacancy_loss +
            monthly_management_fee
        )

        # 7. 月现金流
        monthly_cashflow = rent - total_monthly_expenses
        annual_cashflow = monthly_cashflow * 12

        # 8. 现金回报率 = 年现金流 / 首付金额
        down_payment = price * self.down_payment_percent
        cash_on_cash_return = (annual_cashflow / down_payment) * 100 if down_payment > 0 else 0

        # 9. 盈亏平衡比率 = 总支出 / 毛收入
        break_even_ratio = (total_monthly_expenses / rent) * 100 if rent > 0 else 0

        # 10. 投资评级
        investment_grade = self._calculate_grade(cap_rate, cash_on_cash_return, break_even_ratio)

        return InvestmentAnalysis(
            cap_rate=round(cap_rate, 2),
            gross_rent_multiplier=round(gross_rent_multiplier, 2),
            monthly_cashflow=round(monthly_cashflow, 2),
            annual_cashflow=round(annual_cashflow, 2),
            cash_on_cash_return=round(cash_on_cash_return, 2),
            price_per_sqft=round(price_per_sqft, 2),
            rent_per_sqft=round(rent_per_sqft, 2),
            break_even_ratio=round(break_even_ratio, 2),
            investment_grade=investment_grade
        )

    def _calculate_grade(
        self,
        cap_rate: float,
        cash_on_cash_return: float,
        break_even_ratio: float
    ) -> str:
        """
        计算投资评级

        A: 优秀投资
        B: 良好投资
        C: 一般投资
        D: 风险投资
        """
        score = 0

        # CAP Rate 评分
        if cap_rate >= 8:
            score += 3
        elif cap_rate >= 6:
            score += 2
        elif cap_rate >= 4:
            score += 1

        # 现金回报率评分
        if cash_on_cash_return >= 15:
            score += 3
        elif cash_on_cash_return >= 8:
            score += 2
        elif cash_on_cash_return >= 0:
            score += 1

        # 盈亏平衡比率评分（越低越好）
        if break_even_ratio <= 70:
            score += 3
        elif break_even_ratio <= 85:
            score += 2
        elif break_even_ratio <= 100:
            score += 1

        # 综合评级
        if score >= 8:
            return "A"
        elif score >= 6:
            return "B"
        elif score >= 4:
            return "C"
        else:
            return "D"


# 全局计算器实例
investment_calculator = InvestmentCalculator()
