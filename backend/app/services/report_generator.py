"""
PDF报告生成服务
生成专业的房产投资分析报告
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import Dict, Any, Optional
from datetime import datetime
import io
import os


class ReportGenerator:
    """PDF报告生成器"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """设置自定义样式"""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2563eb')
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#1e40af'),
            borderPadding=5,
        ))

        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            leading=14,
        ))

        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#059669'),
            spaceAfter=6,
        ))

        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#dc2626'),
            spaceAfter=6,
        ))

    def generate_report(
        self,
        property_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        market_insights: Dict[str, Any],
        user_name: Optional[str] = None
    ) -> bytes:
        """
        生成PDF报告

        Args:
            property_data: 房产信息
            analysis_data: 投资分析数据
            market_insights: 市场洞察
            user_name: 用户名

        Returns:
            PDF文件的字节内容
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        # 标题
        story.append(Paragraph("PropertyPulse", self.styles['ReportTitle']))
        story.append(Paragraph("Real Estate Investment Analysis Report", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['ReportBody']))
        if user_name:
            story.append(Paragraph(f"Prepared for: {user_name}", self.styles['ReportBody']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb')))
        story.append(Spacer(1, 20))

        # 房产概览
        story.append(Paragraph("Property Overview", self.styles['SectionHeader']))

        overview_data = [
            ['Address', property_data.get('address', 'N/A')],
            ['City, State', f"{property_data.get('city', 'N/A')}, {property_data.get('state', 'N/A')}"],
            ['Property Type', property_data.get('property_type', 'N/A')],
            ['Year Built', str(property_data.get('year_built', 'N/A'))],
            ['Square Feet', f"{property_data.get('square_feet', 'N/A'):,}" if property_data.get('square_feet') else 'N/A'],
            ['Bedrooms', str(property_data.get('bedrooms', 'N/A'))],
            ['Bathrooms', str(property_data.get('bathrooms', 'N/A'))],
        ]

        overview_table = Table(overview_data, colWidths=[2*inch, 4.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 20))

        # 价格信息
        story.append(Paragraph("Price & Rent Analysis", self.styles['SectionHeader']))

        price_data = [
            ['Metric', 'Value'],
            ['Estimated Price', self._format_currency(property_data.get('price_estimate'))],
            ['Estimated Monthly Rent', self._format_currency(property_data.get('rent_estimate'))],
            ['Price per Sq Ft', f"${analysis_data.get('price_per_sqft', 0):,.2f}" if analysis_data.get('price_per_sqft') else 'N/A'],
            ['Rent per Sq Ft', f"${analysis_data.get('rent_per_sqft', 0):,.2f}" if analysis_data.get('rent_per_sqft') else 'N/A'],
            ['Gross Rent Multiplier', f"{analysis_data.get('gross_rent_multiplier', 0):.1f} years"],
        ]

        price_table = Table(price_data, colWidths=[3*inch, 3.5*inch])
        price_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(price_table)
        story.append(Spacer(1, 20))

        # 投资分析
        story.append(Paragraph("Investment Analysis", self.styles['SectionHeader']))

        # 投资评级高亮
        grade = analysis_data.get('investment_grade', 'N/A')
        grade_color = self._get_grade_color(grade)
        story.append(Paragraph(
            f"<b>Investment Grade: {grade}</b> - {self._get_grade_description(grade)}",
            self.styles['Highlight'] if grade in ['A', 'B'] else self.styles['Warning']
        ))
        story.append(Spacer(1, 10))

        analysis_data_rows = [
            ['Metric', 'Value', 'Assessment'],
            ['CAP Rate', f"{analysis_data.get('cap_rate', 0):.2f}%", self._assess_cap_rate(analysis_data.get('cap_rate', 0))],
            ['Monthly Cash Flow', self._format_currency(analysis_data.get('monthly_cashflow')), self._assess_cashflow(analysis_data.get('monthly_cashflow', 0))],
            ['Annual Cash Flow', self._format_currency(analysis_data.get('annual_cashflow')), ''],
            ['Cash on Cash Return', f"{analysis_data.get('cash_on_cash_return', 0):.2f}%", self._assess_coc_return(analysis_data.get('cash_on_cash_return', 0))],
            ['Break Even Ratio', f"{analysis_data.get('break_even_ratio', 0):.1f}%", self._assess_break_even(analysis_data.get('break_even_ratio', 0))],
        ]

        analysis_table = Table(analysis_data_rows, colWidths=[2*inch, 2*inch, 2.5*inch])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ]))
        story.append(analysis_table)
        story.append(Spacer(1, 20))

        # 市场洞察
        story.append(Paragraph("Market Insights", self.styles['SectionHeader']))

        insights = market_insights.get('insights', [])
        for insight in insights:
            icon = self._get_insight_icon(insight.get('type', 'info'))
            story.append(Paragraph(
                f"{icon} <b>{insight.get('title', '')}</b>: {insight.get('description', '')}",
                self.styles['ReportBody']
            ))

        story.append(Spacer(1, 20))

        # 投资建议
        story.append(Paragraph("Recommendation", self.styles['SectionHeader']))
        recommendation = market_insights.get('recommendation', 'N/A')
        rec_style = self.styles['Highlight'] if recommendation == '建议购买' else self.styles['ReportBody']
        story.append(Paragraph(f"<b>{recommendation}</b>", rec_style))

        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 10))

        # 免责声明
        story.append(Paragraph(
            "<i>Disclaimer: This report is for informational purposes only and does not constitute financial advice. "
            "All data and estimates are based on available information and may not reflect actual market conditions. "
            "Please consult with a licensed real estate professional before making investment decisions.</i>",
            ParagraphStyle(
                name='Disclaimer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#6b7280'),
            )
        ))

        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Generated by PropertyPulse | propertypulse.com",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#9ca3af'),
                alignment=TA_CENTER,
            )
        ))

        # 构建PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def _format_currency(self, value: Optional[float]) -> str:
        """格式化货币"""
        if value is None:
            return 'N/A'
        return f"${value:,.0f}"

    def _get_grade_color(self, grade: str) -> str:
        """获取评级颜色"""
        colors_map = {
            'A': '#059669',
            'B': '#2563eb',
            'C': '#d97706',
            'D': '#dc2626',
        }
        return colors_map.get(grade, '#6b7280')

    def _get_grade_description(self, grade: str) -> str:
        """获取评级描述"""
        descriptions = {
            'A': 'Excellent Investment Opportunity',
            'B': 'Good Investment Potential',
            'C': 'Fair Investment - Requires Careful Evaluation',
            'D': 'High Risk Investment - Proceed with Caution',
        }
        return descriptions.get(grade, 'Not Available')

    def _assess_cap_rate(self, cap_rate: float) -> str:
        """评估CAP Rate"""
        if cap_rate >= 8:
            return 'Excellent'
        elif cap_rate >= 6:
            return 'Good'
        elif cap_rate >= 4:
            return 'Fair'
        else:
            return 'Below Market'

    def _assess_cashflow(self, cashflow: float) -> str:
        """评估现金流"""
        if cashflow > 500:
            return 'Strong Positive'
        elif cashflow > 0:
            return 'Positive'
        elif cashflow > -500:
            return 'Slight Negative'
        else:
            return 'Negative'

    def _assess_coc_return(self, coc: float) -> str:
        """评估现金回报率"""
        if coc >= 15:
            return 'Excellent'
        elif coc >= 8:
            return 'Good'
        elif coc >= 0:
            return 'Fair'
        else:
            return 'Negative'

    def _assess_break_even(self, ratio: float) -> str:
        """评估盈亏平衡比率"""
        if ratio <= 70:
            return 'Excellent'
        elif ratio <= 85:
            return 'Good'
        elif ratio <= 100:
            return 'Tight'
        else:
            return 'Cash Negative'

    def _get_insight_icon(self, insight_type: str) -> str:
        """获取洞察图标"""
        icons = {
            'positive': '[+]',
            'warning': '[!]',
            'neutral': '[i]',
            'info': '[i]',
        }
        return icons.get(insight_type, '[i]')


# 全局实例
report_generator = ReportGenerator()
