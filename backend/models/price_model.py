from pydantic import BaseModel
from typing import List, Optional

class PricePoint(BaseModel):
    """Single price data point"""
    date: str
    farmgate: float
    retail: float
    margin: float
    farmer_share: float

class PriceSummary(BaseModel):
    """Summary statistics for prices"""
    avg_farmgate: float
    avg_retail: float
    avg_margin: float
    avg_farmer_share: float
    max_margin: float
    min_margin: float
    data_points: int

class PriceResponse(BaseModel):
    """Response format for price data"""
    commodity: str
    data: List[PricePoint]
    summary: Optional[PriceSummary] = None

class MarginAnalysisResult(BaseModel):
    """Marketing margin analysis results"""
    commodity: str
    data: List[PricePoint]

class GrangerResult(BaseModel):
    """Granger causality test results"""
    commodity: str
    p_value: float
    is_significant: bool
    interpretation: str
    message: str
    correlation: Optional[float] = None
    price_change_correlation: Optional[float] = None

class TrendResult(BaseModel):
    """Time-series trend analysis"""
    commodity: str
    period_start: str
    period_end: str
    farmgate_growth_percent: float
    retail_growth_percent: float
    farmgate_volatility: float
    retail_volatility: float
    data_points: int