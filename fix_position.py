def calculate_pivot_points(data, pivot_period=14):
    # Вычислить уровни Pivot Points
    close_prices = data['close']
    high_prices = data['high']
    low_prices = data['low']

    pivot = (high_prices + low_prices + close_prices) / 3
    r1 = 2 * pivot - low_prices
    s1 = 2 * pivot - high_prices
    r2 = pivot + (high_prices - low_prices)
    s2 = pivot - (high_prices - low_prices)
    r3 = high_prices + 2 * (pivot - low_prices)
    s3 = low_prices - 2 * (high_prices - pivot)

    return pivot, r1, s1, r2, s2, r3, s3

def choose_stop_loss_pivot(data, order_type, pivot_period=14, risk_preference=3):
    pivot, r1, s1, r2, s2, r3, s3 = calculate_pivot_points(data, pivot_period)

    if order_type == "LONG":
        if risk_preference == 1:
            chosen_stop_loss = s1  # Низкий риск - выбираем S1
        elif risk_preference == 2:
            chosen_stop_loss = s2  # Средний риск - выбираем S2
        elif risk_preference == 3:
            chosen_stop_loss = s3  # Высокий риск - выбираем S3
        else:
            chosen_stop_loss = s2  # По умолчанию, выбираем S2
    elif order_type == "SHORT":
        if risk_preference == 1:
            chosen_stop_loss = r1  # Низкий риск - выбираем R1
        elif risk_preference == 2:
            chosen_stop_loss = r2  # Средний риск - выбираем R2
        elif risk_preference == 3:
            chosen_stop_loss = r3  # Высокий риск - выбираем R3
        else:
            chosen_stop_loss = r2  # По умолчанию, выбираем R2
    else:
        # По умолчанию, выбираем S2 (для LONG) или R2 (для SHORT)
        chosen_stop_loss = s2 if order_type == "LONG" else r2

    return chosen_stop_loss[-1]