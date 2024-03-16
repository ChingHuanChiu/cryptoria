from enum import Enum, unique

@unique
class SystemMessageEnum(Enum):

    BEGIN_MESSAGE = "******交易監控開始******"
    END_MESSAGE = "******交易結束******"


@unique
class OrderStatusEnum(Enum):

    SUCCESS = "SUCESS"
    FAIL = "FAIL"


@unique
class TradingDirection(Enum):

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@unique
class PositionStatus(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    EMPTY = "EMPTY"


@unique
class OrderType(Enum):
    # TODO: make clear the difference
    ORDER_TYPE_LIMIT = 'LIMIT'
    ORDER_TYPE_MARKET = 'MARKET'
    ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
    ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'


@unique
class TimeInForce(Enum):
    TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
    TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
    TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill
    TIME_IN_FORCE_GTX = 'GTX'  # Post only order


@unique 
class KLineInterval(Enum):
    KLINE_INTERVAL_1SECOND = '1s'
    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'


@unique
class HistoricalKlinesType(Enum):
    SPOT = 1
    FUTURES = 2
    FUTURES_COIN = 3