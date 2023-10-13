"""
🔴<b>SHORT</b> - #LPTUSDT

✅<b>ЦЕНА ВХОДА</b>: $5.8

💰<b>ТЕЙК-ПРОФИТ</b>:
5.651079684587697

🛑<b>СТОП-ЛОСС</b>:
$5.894349897654854

🎯<b>ЦЕЛЬ 1</b>:
$5.7627699211469245

🎯<b>ЦЕЛЬ 2</b>:
$5.734847362007118

🎯<b>ЦЕЛЬ 3</b>:
$5.713905442652263

🎯<b>ЦЕЛЬ 4</b>:
$5.698199003136121

🕒<b>ВРЕМЯ СИГНАЛА</b>:
2023-10-10 16:57
_____

<b>ПОТЕНЦИАЛЬНАЯ ПРИБЫЛЬ</b>:
0,2%

<b>ПОТЕНЦИАЛЬНАЯ ПОТЕРЯ</b>:
0,2%

*Сигнал замечен на тф 1 час

"""


"""

stop_loss_price = predicted_values['yhat_lower'].iloc[-1]
                stop_loss_forecasts = forecast_stop_loss(historical_data, "LONG", num_values=3) 
                stop_losses = [stop_loss_forecasts[0], stop_loss_forecasts[1], stop_loss_forecasts[2]]

stop_loss_price = predicted_values['yhat_upper'].iloc[-1]
stop_loss_forecasts = forecast_stop_loss(historical_data, "SHORT", num_values=3) 
stop_losses = [stop_loss_forecasts[0], stop_loss_forecasts[1], stop_loss_forecasts[2]]
"""



"""
                # take_profit_points = forecast_take_profit_price_long(historical_data, 150)
                # take_profit_points = [take_profit_points[146], take_profit_points[147], take_profit_points[148], take_profit_points[149]]
                # take_profit_points.sort()
                #take_profit_price = predicted_values['yhat_upper'].iloc[-1]
                # take_profit_price = take_profit_points[3]
                #long_fixations = fix_position_long(entry_price, take_profit_price)







                                #stop_loss_price = calculate_stop_loss(historical_data, atr_period, atr_multiplier)
                # if stop_loss_price < entry_price:
                #take_profit_price = predicted_values['yhat_lower'].iloc[-1]
                # take_profit_points = forecast_take_profit_price_short(historical_data, 150)
                # take_profit_points = [take_profit_points[146], take_profit_points[147], take_profit_points[148], take_profit_points[149]]
                # take_profit_points.sort()
                # take_profit_price = take_profit_points[0]


"""