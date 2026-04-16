TEXTS = {
    "ua": {
        "start": "Вітаю 👋\nОбери дію:",
        "choose_lang": "Оберіть мову:",
        "language_changed": "✅ Мову змінено",

        "no_access": "⛔ У тебе немає активного доступу.",
        "activate_access_first": "⛔ Спочатку активуй доступ через /start",
        "no_active_access_start": "⛔ У тебе немає активного доступу. Натисни /start",

        "choose_period": "Обери період статистики:",
        "choose_full_stats_period": "Обери період для повної статистики:",
        "choose_analytics_period": "Обери період для аналітики:",
        "enter_promo_hint": "Введи промокод одним повідомленням:",

        "daily_limit_reached": (
            "⛔ Денний ліміт вичерпано.\n\n"
            "Твій тариф дозволяє {limit} скрінів на добу.\n"
            "Спробуй знову завтра."
        ),

        "send_screen_with_limit": (
            "📤 Надішли скрін ставки\n\n"
            "Ліміт на сьогодні: {limit}\n"
            "Використано: {used}\n"
            "Залишилось: {remaining}"
        ),

        "account_info": (
            "📈 Інформація по акаунту\n\n"
            "Тариф: {plan}\n"
            "Доступ до: {access_until}\n\n"
            "Ліміт скрінів на добу: {limit}\n"
            "Використано сьогодні: {used}\n"
            "Залишилось сьогодні: {remaining}"
        ),

        "stats_result": (
            "📊 Моя статистика ({period})\n\n"
            "💰 Прибуток: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 % виграшних ставок: {win_rate}%\n"
            "📊 Середній коеф: {avg_odds}\n\n"
            "🔥 Серія: {win_streak}"
        ),

        "full_stats_result": (
            "📈 Повна статистика ({period})\n\n"
            "💰 Прибуток: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 % виграшних ставок: {win_rate}%\n"
            "📊 Середній коеф: {avg_odds}\n\n"
            "📦 Всього ставок: {total_bets}\n"
            "✅ Виграшних: {wins}\n"
            "❌ Програшних: {losses}\n"
            "🔁 Повернень: {refunds}\n\n"
            "💵 Сума ставок: {total_stake}\n"
            "🔥 Поточна серія перемог: {win_streak}\n"
            "🏆 Найкраща серія за період: {best_win_streak}\n\n"
            "📌 Типи ставок:\n"
            "На тотал: {total_type_count}\n"
            "На результат: {result_type_count}\n\n"
            "📊 По типах (+/-):\n"
            "Тотал → {total_type_profit}\n"
            "Результат → {result_type_profit}\n\n"
            "📈 По коефіцієнтах (+/-):\n"
            "<2 → {under_2_count} ставок ({under_2_profit})\n"
            "≥2 → {over_2_count} ставок ({over_2_profit})\n\n"
            "📉 Останні 5 ставок:\n"
            "{last_results}"
        ),

        "analytics_result": (
            "🧠 Аналітика ({period})\n\n"
            "📊 Розподіл:\n"
            "Тотал: {total_type_count}\n"
            "Результат: {result_type_count}\n\n"
            "💵 Прибуток:\n"
            "Тотал → {total_type_profit}\n"
            "Результат → {result_type_profit}\n\n"
            "📈 По коефіцієнтах:\n"
            "<2 → {under_2_count} ставок ({under_2_profit})\n"
            "≥2 → {over_2_count} ставок ({over_2_profit})\n\n"
            "🎯 Виграш:\n"
            "{win_rate}%\n\n"
            "🏆 Найефективніше:\n"
            "{best_type}\n\n"
            "⚠️ Слабке місце:\n"
            "{worst_type}\n\n"
            "📌 Висновок:\n"
            "{conclusion}\n\n"
            "{risk_block}\n"
            "{dynamics_block}\n\n"
            "🧠 Твій стиль:\n"
            "{profile_title}\n\n"
            "📌 Характеристика:\n"
            "{profile_desc}"
        ),

        "bet_type_total": "Тотал",
        "bet_type_result": "Результат",
        "bet_type_equal": "Однаково",
        "bet_type_none": "Немає явного слабкого місця",
        "market_type_1x2": "1X2",
        "market_type_total": "Тотал",
        "market_type_btts": "Обидві заб'ють",
        "market_type_handicap": "Фора",
        "market_type_double_chance": "1X/2X",
        "market_type_corners": "Кутові",
        "market_type_cards": "Картки",
        "market_type_other": "Інше",

        "conclusion_better_total": "Ти стабільно заробляєш на тоталах.",
        "conclusion_better_result": "Краще працюють ставки на результат.",
        "conclusion_equal": "По типах ставок баланс рівний.",

        "conclusion_good": "У тебе хороша динаміка та контроль гри.",
        "conclusion_neutral": "Результат стабільний, але є потенціал росту.",
        "conclusion_bad": "Результати просідають — варто переглянути стратегію.",

        "coeff_under2": "Краще фокусуватись на коефіцієнтах <2.",
        "coeff_over2": "Краще працюють коефіцієнти ≥2.",
        "coeff_under_2": "Краще працюють коефіцієнти <2.",
        "coeff_over_2": "Краще працюють коефіцієнти ≥2.",

        "risk_losing_streak": "⚠️ У тебе серія поразок ({streak}). Рекомендується зменшити розмір ставки.",
        "risk_roi_drop": "⚠️ Прибуток за останні 3 дні знизився порівняно з попередніми 3 днями.",
        "analytics_dynamics": "📈 Динаміка:\nОстанні 3 дні: {recent_profit}\nПопередні 3 дні: {previous_profit}",

        "profile_careful_title": "Обережний гравець",
        "profile_careful_desc": "Ти частіше граєш коефіцієнти до 2. Це дає стабільніший, але повільніший ріст.",
        "profile_aggressive_title": "Агресивний гравець",
        "profile_aggressive_desc": "Ти часто граєш коефіцієнти 2 і вище. Це підвищує ризик і робить результат менш стабільним.",
        "profile_balanced_title": "Збалансований гравець",
        "profile_balanced_desc": "Ти рівномірно використовуєш різні коефіцієнти. Баланс хороший, але варто перевіряти, що реально дає прибуток.",
        "profile_mixed_title": "Змішаний стиль",
        "profile_mixed_desc": "Ти комбінуєш різні підходи та коефіцієнти.",
        "profile_system_title": "Системний стиль",
        "profile_system_desc": "Ти дотримуєшся стабільної та дисциплінованої гри.",

        "full_stats_result_basic": "📈 Повна статистика ({period})\n\n💰 Фінальний результат\nПрибуток: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\nСередній коеф: {avg_odds}\n\n📦 Активність\nВсього ставок: {total_bets}\nРозрахованих: {settled_bets}\nОчікують результат: {pending_bets}\n\n✅ Виграші: {wins}\n❌ Програші: {losses}\n➖ Повернення: {refunds}\n\n💵 Загальна сума ставок: {total_stake}\n💵 Сума розрахованих ставок: {settled_stake}\n\n🔥 Серії\nПоточна серія перемог: {current_win_streak}\nНайкраща серія перемог: {best_win_streak}\nНайгірша серія поразок: {worst_lose_streak}\n\n🎯 По типах ставок\nТотали: {total_type_count} | {total_type_profit}\nРезультат: {result_type_count} | {result_type_profit}\n\n📈 По коефіцієнтах\n<2.0 : {odds_lt2_count} ставок | {odds_lt2_profit}\n2.0–2.49 : {odds_mid_count} ставок | {odds_mid_profit}\n2.5+ : {odds_high_count} ставок | {odds_high_profit}\n\n🕓 Останні 5 результатів\n{last_results}",
        "full_stats_result_vip": "📈 VIP Повна статистика ({period})\n\n💰 Фінальний результат\nПрибуток: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\nСередній коеф: {avg_odds}\n\n📦 Активність\nВсього ставок: {total_bets}\nРозрахованих: {settled_bets}\nОчікують результат: {pending_bets}\n\n✅ Виграші: {wins}\n❌ Програші: {losses}\n➖ Повернення: {refunds}\n\n💵 Загальна сума ставок: {total_stake}\n💵 Сума розрахованих ставок: {settled_stake}\n\n🔥 Серії\nПоточна серія перемог: {current_win_streak}\nНайкраща серія перемог: {best_win_streak}\nНайгірша серія поразок: {worst_lose_streak}\n\n🎯 По типах ставок\nТотали: {total_type_count} | прибуток {total_type_profit} | ROI {total_type_roi}%\nРезультат: {result_type_count} | прибуток {result_type_profit} | ROI {result_type_roi}%\n\n📈 По коефіцієнтах\n<2.0 : {odds_lt2_count} ставок | {odds_lt2_profit} | ROI {odds_lt2_roi}%\n2.0–2.49 : {odds_mid_count} ставок | {odds_mid_profit} | ROI {odds_mid_roi}%\n2.5+ : {odds_high_count} ставок | {odds_high_profit} | ROI {odds_high_roi}%\n\n🕓 Останні 5 результатів\n{last_results}",
        "analytics_result_basic": "🧠 Аналітика ({period})\n\n📌 Загальна оцінка\n{overall_title}\n{overall_desc}\n\n💰 Основні цифри\nПрибуток: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\n\n🏆 Що працює найкраще\nТип ставок: {best_type}\nROI: {best_type_roi}%\n\nКоефіцієнти: {best_odds_bucket}\nWin rate: {best_odds_win_rate}%\nROI: {best_odds_roi}%\n\n📉 Що просідає\n{weak_spot_text}\n\n📈 Динаміка\n{dynamics_text}\n{trend_text}\n\n🧠 Профіль гравця\n{profile_title}\n\n{profile_desc}\n\n⚠️ Увага\n{risk_block}\n\n{vip_teaser}",
        "analytics_result_vip": "🧠 VIP Аналітика ({period})\n\n📌 Загальний підсумок\n{overall_title}\n{overall_desc}\n💰 Прибуток: {net_profit}\n📈 ROI: {roi}%\n🎯 Win rate: {win_rate}%\n📦 Settled bets: {settled_bets}\n\n📊 По типах ставок\n{total_breakdown}\n{result_breakdown}\n\n📈 По коефіцієнтах\n{odds_lt2_breakdown}\n{odds_mid_breakdown}\n{odds_high_breakdown}\n\n📉 Стабільність\n{stability_block}\n\n📈 Динаміка\n{dynamics_text}\n\n🧠 Профіль\n{profile_title}\n{profile_desc}\n\n✅ Сильні сторони\n{strengths_block}\n\n⚠️ Слабкі місця\n{weak_spot_text}\n\n🚨 Ризики\n{risk_block}\n\n📌 Рекомендація\n{recommendation_text}",
        "analytics_odds_bucket_lt2": "<2.0",
        "analytics_odds_bucket_mid": "2.0–2.49",
        "analytics_odds_bucket_high": "2.5+",
        "analytics_odds_bucket_none": "Недостатньо даних",
        "analytics_status_great_title": "Результат: дуже хороший",
        "analytics_status_great_desc": "Ти в плюсі та показуєш сильну динаміку.",
        "analytics_status_good_title": "Результат: хороший",
        "analytics_status_good_desc": "Ти граєш стабільно і контролюєш дистанцію.",
        "analytics_status_neutral_title": "Результат: нейтральний",
        "analytics_status_neutral_desc": "Є база, але ще можна покращити якість гри.",
        "analytics_status_bad_title": "Результат: слабкий",
        "analytics_status_bad_desc": "Зараз аналітика показує точки, де варто зменшити ризик.",
        "analytics_compare_block": "{current_label}: {current_profit} | ROI {current_roi}% | WR {current_wr}%\n{previous_label}: {previous_profit} | ROI {previous_roi}% | WR {previous_wr}%",
        "analytics_type_breakdown_line": "{label} → {count} ставок | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_odds_breakdown_line": "{bucket} → {count} ставок | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_market_breakdown_line": "{label} → {count} ставок | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_no_market_data": "Недостаточно данных по типам ставок.",
        "analytics_weak_market_line": "Тип рынка: {label} | ROI {roi}% | Profit {profit}",
        "analytics_strength_market": "— сильный рынок: {label}",
        "analytics_market_breakdown_line": "{label} → {count} ставок | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_no_market_data": "Недостатньо даних по типах ставок.",
        "analytics_weak_market_line": "Тип ринку: {label} | ROI {roi}% | Profit {profit}",
        "analytics_strength_market": "— сильний ринок: {label}",
        "analytics_stability_block": "Поточна серія перемог: {current_win_streak}\nНайкраща серія перемог: {best_win_streak}\nНайгірша серія поразок: {worst_lose_streak}",
        "analytics_weak_type_line": "Тип ставок: {label} | ROI {roi}% | Profit {profit}",
        "analytics_weak_odds_line": "Коефіцієнти: {label} | ROI {roi}% | Profit {profit}",
        "analytics_no_weak_spot": "Явного слабкого місця поки не видно.",
        "analytics_strength_type": "— найкраще працює тип ставок: {label}",
        "analytics_strength_odds": "— сильний сегмент коефіцієнтів: {label}",
        "analytics_no_strengths": "Поки що даних недостатньо для сильних висновків.",
        "analytics_trend_up": "Твоя форма покращується 📈",
        "analytics_trend_down": "Останній відрізок слабший за попередній 📉",
        "analytics_trend_flat": "Динаміка близька до стабільної ➖",
        "analytics_risk_losing_streak": "— була серія поразок: {streak}",
        "analytics_risk_negative_roi": "— загальний ROI зайшов у помітний мінус",
        "analytics_risk_high_odds_drag": "— коефіцієнти 2.5+ тягнуть результат вниз",
        "analytics_risk_low_winrate": "— win rate нижчий за безпечний рівень",
        "analytics_risk_downtrend": "— останній відрізок гірший за попередній",
        "analytics_no_risks": "Сильних ризиків за вибраний період не виявлено.",
        "analytics_recommendation_cut_high_odds": "Скороти частку ставок з коефіцієнтами 2.5+ і сфокусуйся на стабільніших сегментах.",
        "analytics_recommendation_focus_total": "Найближчим часом краще змістити фокус у бік тоталів — вони дають кращий результат.",
        "analytics_recommendation_focus_result": "Зараз результативніші ставки на результат — варто підсилити саме цей напрямок.",
        "analytics_recommendation_reduce_risk": "При серії поразок зменшуй ризик і не підвищуй агресивність гри.",
        "analytics_recommendation_keep_discipline": "Продовжуй поточну дисципліну й спостерігай, який сегмент ставок тримає ROI вище.",
        "analytics_vip_teaser": "🔓 У VIP доступно:\n• ROI по кожному типу ставок\n• Розширена динаміка\n• Персональні рекомендації\n• Глибокий аналіз стилю гри",
        "period_recent_3days": "Останні 3 дні",
        "period_previous_3days": "Попередні 3 дні",
        "period_previous_week": "Попередній тиждень",
        "period_previous_month": "Попередній місяць",

        "period_today": "Сьогодні",
        "period_yesterday": "Вчора",
        "period_3days": "Останні 3 дні",
        "period_7days": "Останні 7 днів",
        "period_30days": "Останні 30 днів",
        "period_current_week": "Поточний тиждень",
        "period_current_month": "Поточний місяць",

        "promo_not_found": "❌ Промокод не знайдено, неактивний або вже використаний.",
        "promo_cancelled": "Введення промокоду скасовано.",
        "promo_activated": (
            "✅ Промокод активовано.\n"
            "Тариф: {plan}\n"
            "Доступ відкрито на {days} днів."
        ),

        "choose_access_option": "Оберіть один з варіантів доступу:",
        "usdt_choose_plan": "Оберіть тариф для оплати через USDT TRC20:",
        "usdt_wallet_not_configured": "TRC20 гаманець не налаштований у .env",
        "usdt_send_screenshot": "📸 Тепер скинь скрін переказу.",
        "usdt_choose_plan_first": "Спочатку обери тариф.",
        "usdt_screenshot_received": (
            "✅ Скрін отримано.\n\n"
            "Тепер натисни кнопку 'Я оплатив'."
        ),
        "usdt_no_pending_payment": (
            "Не знайдено активної заявки на оплату. Спочатку обери тариф."
        ),
        "usdt_payment_sent": (
            "✅ Заявка на перевірку оплати прийнята.\n\n"
            "Після перевірки ти отримаєш промокод від адміністратора."
        ),

        "stars_choose_plan": "Оберіть тариф для оплати через Telegram Stars:",
        "stars_plan_not_found": "Оплата отримана, але тариф не знайдено.",
        "stars_payment_success_7days": "✅ Оплата успішна. Бот активний на 7 днів.",
        "stars_payment_success": (
            "✅ Оплата успішна.\n"
            "Тариф: {title}\n"
            "Доступ активовано на {days} днів."
        ),

        "bet_analysis_started": "🤖 Аналізую ставку.",
        "bet_saved": (
            "✅ Ставку розпізнано і збережено\n\n"
            "🎯 Результат: {bet_result}\n"
            "📌 Тип ставки: {bet_type}\n"
            "💰 Сума ставки: {stake_amount}\n"
            "📊 Коефіцієнт: {odds}\n\n"
            "📤 Можеш надсилати наступний скрін\n"
            "Залишилось сьогодні: {remaining}/{limit}"
        ),
        "bet_pending_saved": (
            "🕒 Ставку збережено як нерозраховану\n\n"
            "📌 Тип ставки: {bet_type}\n"
            "💰 Сума ставки: {stake_amount}\n"
            "📊 Коефіцієнт: {odds}\n\n"
            "Після розрахунку надішли фінальний скрін цієї ставки\n"
            "Залишилось сьогодні: {remaining}/{limit}"
        ),
        "bet_parse_failed": (
            "❌ Не вдалося розпізнати ставку зі скріна.\n"
            "Спробуй інший скрін або надішли чіткіший."
        ),

        "bet_result_win": "виграш",
        "bet_result_lose": "програш",
        "bet_result_refund": "повернення",
        "bet_result_pending": "нерозрахована",

        "trial_intro_push": (
            "🚀 Пробний доступ активовано!\n\n"
            "⚠️ У тебе є 10 аналізів на день\n\n"
            "📊 Що ти побачиш:\n"
            "• свій реальний ROI\n"
            "• де ти втрачаєш гроші\n"
            "• які ставки працюють краще\n\n"
            "👇 Надішли перший скрін"
        ),
        "trial_after_first_push": (
            "📊 Перший результат уже є.\n\n"
            "Навіть 1 скрін уже показує більше, ніж більшість гравців бачать за тиждень.\n\n"
            "👉 Надішли ще кілька ставок — зберемо повну картину."
        ),
        "trial_after_third_push": (
            "📊 У тебе вже є перші дані для висновків.\n\n"
            "❌ Більшість гравців не знають свій реальний ROI\n"
            "✅ Ти вже бачиш те, що зазвичай приховано\n\n"
            "🔥 Ще трохи — і картина по ставках стане очевидною."
        ),
        "trial_limit_push": (
            "❌ Ліміт досягнуто ({used}/{limit})\n\n"
            "📊 Ти вже побачив базову цінність бота.\n"
            "Уяви, що буде, якщо відстежувати це щодня.\n\n"
            "🔥 Відкрий повний доступ і масштабуй результат."
        ),
        "buy_access_push": (
            "🚀 Повний доступ дає:\n\n"
            "📊 Повну статистику\n"
            "🧠 Глибоку аналітику\n"
            "📈 Контроль ROI і прибутку\n"
            "🔥 Виявлення слабких місць\n\n"
            "👇 Обери тариф"
        )
    },

    "ru": {
        "start": "Привет 👋\nВыбери действие:",
        "choose_lang": "Выберите язык:",
        "language_changed": "✅ Язык изменён",

        "no_access": "⛔ У тебя нет активного доступа.",
        "activate_access_first": "⛔ Сначала активируй доступ через /start",
        "no_active_access_start": "⛔ У тебя нет активного доступа. Нажми /start",

        "choose_period": "Выбери период статистики:",
        "choose_full_stats_period": "Выбери период для полной статистики:",
        "choose_analytics_period": "Выбери период для аналитики:",
        "enter_promo_hint": "Введи промокод одним сообщением:",

        "daily_limit_reached": (
            "⛔ Дневной лимит исчерпан.\n\n"
            "Твой тариф позволяет {limit} скринов в сутки.\n"
            "Попробуй снова завтра."
        ),

        "send_screen_with_limit": (
            "📤 Отправь скрин ставки\n\n"
            "Лимит на сегодня: {limit}\n"
            "Использовано: {used}\n"
            "Осталось: {remaining}"
        ),

        "account_info": (
            "📈 Информация по аккаунту\n\n"
            "Тариф: {plan}\n"
            "Доступ до: {access_until}\n\n"
            "Лимит скринов в сутки: {limit}\n"
            "Использовано сегодня: {used}\n"
            "Осталось сегодня: {remaining}"
        ),

        "stats_result": (
            "📊 Моя статистика ({period})\n\n"
            "💰 Прибыль: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 % выигрышных ставок: {win_rate}%\n"
            "📊 Средний коэфф: {avg_odds}\n\n"
            "🔥 Серия: {win_streak}"
        ),

        "full_stats_result": (
            "📈 Полная статистика ({period})\n\n"
            "💰 Прибыль: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 % выигрышных ставок: {win_rate}%\n"
            "📊 Средний коэфф: {avg_odds}\n\n"
            "📦 Всего ставок: {total_bets}\n"
            "✅ Выигрышных: {wins}\n"
            "❌ Проигрышных: {losses}\n"
            "🔁 Возвратов: {refunds}\n\n"
            "💵 Сумма ставок: {total_stake}\n"
            "🔥 Текущая серия побед: {win_streak}\n"
            "🏆 Лучшая серия за период: {best_win_streak}\n\n"
            "📌 Типы ставок:\n"
            "На тотал: {total_type_count}\n"
            "На результат: {result_type_count}\n\n"
            "📊 По типам (+/-):\n"
            "Тотал → {total_type_profit}\n"
            "Результат → {result_type_profit}\n\n"
            "📈 По коэффициентам (+/-):\n"
            "<2 → {under_2_count} ставок ({under_2_profit})\n"
            "≥2 → {over_2_count} ставок ({over_2_profit})\n\n"
            "📉 Последние 5 ставок:\n"
            "{last_results}"
        ),

        "analytics_result": (
            "🧠 Аналитика ({period})\n\n"
            "📊 Распределение:\n"
            "Тотал: {total_type_count}\n"
            "Результат: {result_type_count}\n\n"
            "💵 Прибыль:\n"
            "Тотал → {total_type_profit}\n"
            "Результат → {result_type_profit}\n\n"
            "📈 По коэффициентам:\n"
            "<2 → {under_2_count} ставок ({under_2_profit})\n"
            "≥2 → {over_2_count} ставок ({over_2_profit})\n\n"
            "🎯 Выигрыш:\n"
            "{win_rate}%\n\n"
            "🏆 Самое эффективное:\n"
            "{best_type}\n\n"
            "⚠️ Слабое место:\n"
            "{worst_type}\n\n"
            "📌 Вывод:\n"
            "{conclusion}\n\n"
            "{risk_block}\n"
            "{dynamics_block}\n\n"
            "🧠 Твой стиль:\n"
            "{profile_title}\n\n"
            "📌 Характеристика:\n"
            "{profile_desc}"
        ),

        "bet_type_total": "Тотал",
        "bet_type_result": "Результат",
        "bet_type_equal": "Одинаково",
        "bet_type_none": "Нет явного слабого места",
        "market_type_1x2": "1X2",
        "market_type_total": "Тотал",
        "market_type_btts": "Обе забьют",
        "market_type_handicap": "Фора",
        "market_type_double_chance": "1X/2X",
        "market_type_corners": "Угловые",
        "market_type_cards": "Карточки",
        "market_type_other": "Другое",

        "conclusion_better_total": "Ты стабильно зарабатываешь на тоталах.",
        "conclusion_better_result": "Лучше работают ставки на результат.",
        "conclusion_equal": "По типам ставок баланс равный.",

        "conclusion_good": "У тебя хорошая динамика и контроль.",
        "conclusion_neutral": "Результат стабильный, но есть потенциал роста.",
        "conclusion_bad": "Результаты проседают — пересмотри стратегию.",

        "coeff_under2": "Лучше фокусироваться на коэффициентах <2.",
        "coeff_over2": "Лучше работают коэффициенты ≥2.",
        "coeff_under_2": "Лучше работают коэффициенты <2.",
        "coeff_over_2": "Лучше работают коэффициенты ≥2.",

        "risk_losing_streak": "⚠️ У тебя серия поражений ({streak}). Рекомендуется уменьшить размер ставки.",
        "risk_roi_drop": "⚠️ Прибыль за последние 3 дня снизилась по сравнению с предыдущими 3 днями.",
        "analytics_dynamics": "📈 Динамика:\nПоследние 3 дня: {recent_profit}\nПредыдущие 3 дня: {previous_profit}",

        "profile_careful_title": "Осторожный игрок",
        "profile_careful_desc": "Ты чаще играешь коэффициенты до 2. Это дает более стабильный, но более медленный рост.",
        "profile_aggressive_title": "Агрессивный игрок",
        "profile_aggressive_desc": "Ты часто играешь коэффициенты 2 и выше. Это повышает риск и делает результат менее стабильным.",
        "profile_balanced_title": "Сбалансированный игрок",
        "profile_balanced_desc": "Ты равномерно используешь разные коэффициенты. Баланс хороший, но стоит проверять, что реально приносит прибыль.",
        "profile_mixed_title": "Смешанный стиль",
        "profile_mixed_desc": "Ты комбинируешь разные подходы и коэффициенты.",
        "profile_system_title": "Системный стиль",
        "profile_system_desc": "Ты придерживаешься стабильной стратегии.",

        "full_stats_result_basic": "📈 Полная статистика ({period})\n\n💰 Финальный результат\nПрибыль: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\nСредний коэфф: {avg_odds}\n\n📦 Активность\nВсего ставок: {total_bets}\nРассчитанных: {settled_bets}\nОжидают результат: {pending_bets}\n\n✅ Выигрыши: {wins}\n❌ Проигрыши: {losses}\n➖ Возвраты: {refunds}\n\n💵 Общая сумма ставок: {total_stake}\n💵 Сумма рассчитанных ставок: {settled_stake}\n\n🔥 Серии\nТекущая серия побед: {current_win_streak}\nЛучшая серия побед: {best_win_streak}\nХудшая серия поражений: {worst_lose_streak}\n\n🎯 По типам ставок\nТоталы: {total_type_count} | {total_type_profit}\nРезультат: {result_type_count} | {result_type_profit}\n\n📈 По коэффициентам\n<2.0 : {odds_lt2_count} ставок | {odds_lt2_profit}\n2.0–2.49 : {odds_mid_count} ставок | {odds_mid_profit}\n2.5+ : {odds_high_count} ставок | {odds_high_profit}\n\n🕓 Последние 5 результатов\n{last_results}",
        "full_stats_result_vip": "📈 VIP Полная статистика ({period})\n\n💰 Финальный результат\nПрибыль: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\nСредний коэфф: {avg_odds}\n\n📦 Активность\nВсего ставок: {total_bets}\nРассчитанных: {settled_bets}\nОжидают результат: {pending_bets}\n\n✅ Выигрыши: {wins}\n❌ Проигрыши: {losses}\n➖ Возвраты: {refunds}\n\n💵 Общая сумма ставок: {total_stake}\n💵 Сумма рассчитанных ставок: {settled_stake}\n\n🔥 Серии\nТекущая серия побед: {current_win_streak}\nЛучшая серия побед: {best_win_streak}\nХудшая серия поражений: {worst_lose_streak}\n\n🎯 По типам ставок\nТоталы: {total_type_count} | прибыль {total_type_profit} | ROI {total_type_roi}%\nРезультат: {result_type_count} | прибыль {result_type_profit} | ROI {result_type_roi}%\n\n📈 По коэффициентам\n<2.0 : {odds_lt2_count} ставок | {odds_lt2_profit} | ROI {odds_lt2_roi}%\n2.0–2.49 : {odds_mid_count} ставок | {odds_mid_profit} | ROI {odds_mid_roi}%\n2.5+ : {odds_high_count} ставок | {odds_high_profit} | ROI {odds_high_roi}%\n\n🕓 Последние 5 результатов\n{last_results}",
        "analytics_result_basic": "🧠 Аналитика ({period})\n\n📌 Общая оценка\n{overall_title}\n{overall_desc}\n\n💰 Основные цифры\nПрибыль: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\n\n🏆 Что работает лучше всего\nТип ставок: {best_type}\nROI: {best_type_roi}%\n\nКоэффициенты: {best_odds_bucket}\nWin rate: {best_odds_win_rate}%\nROI: {best_odds_roi}%\n\n📉 Что проседает\n{weak_spot_text}\n\n📈 Динамика\n{dynamics_text}\n{trend_text}\n\n🧠 Профиль игрока\n{profile_title}\n\n{profile_desc}\n\n⚠️ Внимание\n{risk_block}\n\n{vip_teaser}",
        "analytics_result_vip": "🧠 VIP Аналитика ({period})\n\n📌 Общий итог\n{overall_title}\n{overall_desc}\n💰 Прибыль: {net_profit}\n📈 ROI: {roi}%\n🎯 Win rate: {win_rate}%\n📦 Settled bets: {settled_bets}\n\n📊 По типам ставок\n{total_breakdown}\n{result_breakdown}\n\n📈 По коэффициентам\n{odds_lt2_breakdown}\n{odds_mid_breakdown}\n{odds_high_breakdown}\n\n📉 Стабильность\n{stability_block}\n\n📈 Динамика\n{dynamics_text}\n\n🧠 Профиль\n{profile_title}\n{profile_desc}\n\n✅ Сильные стороны\n{strengths_block}\n\n⚠️ Слабые места\n{weak_spot_text}\n\n🚨 Риски\n{risk_block}\n\n📌 Рекомендация\n{recommendation_text}",
        "analytics_odds_bucket_lt2": "<2.0",
        "analytics_odds_bucket_mid": "2.0–2.49",
        "analytics_odds_bucket_high": "2.5+",
        "analytics_odds_bucket_none": "Недостаточно данных",
        "analytics_status_great_title": "Результат: очень хороший",
        "analytics_status_great_desc": "Ты в плюсе и показываешь сильную динамику.",
        "analytics_status_good_title": "Результат: хороший",
        "analytics_status_good_desc": "Ты играешь стабильно и контролируешь дистанцию.",
        "analytics_status_neutral_title": "Результат: нейтральный",
        "analytics_status_neutral_desc": "База уже есть, но качество игры можно улучшить.",
        "analytics_status_bad_title": "Результат: слабый",
        "analytics_status_bad_desc": "Сейчас аналитика показывает точки, где стоит снизить риск.",
        "analytics_compare_block": "{current_label}: {current_profit} | ROI {current_roi}% | WR {current_wr}%\n{previous_label}: {previous_profit} | ROI {previous_roi}% | WR {previous_wr}%",
        "analytics_type_breakdown_line": "{label} → {count} ставок | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_odds_breakdown_line": "{bucket} → {count} ставок | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_stability_block": "Текущая серия побед: {current_win_streak}\nЛучшая серия побед: {best_win_streak}\nХудшая серия поражений: {worst_lose_streak}",
        "analytics_weak_type_line": "Тип ставок: {label} | ROI {roi}% | Profit {profit}",
        "analytics_weak_odds_line": "Коэффициенты: {label} | ROI {roi}% | Profit {profit}",
        "analytics_no_weak_spot": "Явного слабого места пока не видно.",
        "analytics_strength_type": "— лучше всего работает тип ставок: {label}",
        "analytics_strength_odds": "— сильный сегмент коэффициентов: {label}",
        "analytics_no_strengths": "Пока данных недостаточно для сильных выводов.",
        "analytics_trend_up": "Твоя форма улучшается 📈",
        "analytics_trend_down": "Последний отрезок слабее предыдущего 📉",
        "analytics_trend_flat": "Динамика близка к стабильной ➖",
        "analytics_risk_losing_streak": "— была серия поражений: {streak}",
        "analytics_risk_negative_roi": "— общий ROI ушёл в заметный минус",
        "analytics_risk_high_odds_drag": "— коэффициенты 2.5+ тянут результат вниз",
        "analytics_risk_low_winrate": "— win rate ниже безопасного уровня",
        "analytics_risk_downtrend": "— последний отрезок хуже предыдущего",
        "analytics_no_risks": "Сильных рисков за выбранный период не обнаружено.",
        "analytics_recommendation_cut_high_odds": "Сократи долю ставок с коэффициентами 2.5+ и сфокусируйся на более стабильных сегментах.",
        "analytics_recommendation_focus_total": "В ближайшее время лучше сместить фокус в сторону тоталов — они дают лучший результат.",
        "analytics_recommendation_focus_result": "Сейчас лучше работают ставки на результат — стоит усилить именно это направление.",
        "analytics_recommendation_reduce_risk": "При серии поражений снижай риск и не повышай агрессивность игры.",
        "analytics_recommendation_keep_discipline": "Сохраняй текущую дисциплину и наблюдай, какой сегмент ставок держит ROI выше.",
        "analytics_vip_teaser": "🔓 В VIP доступно:\n• ROI по каждому типу ставок\n• Расширенная динамика\n• Персональные рекомендации\n• Глубокий анализ стиля игры",
        "period_recent_3days": "Последние 3 дня",
        "period_previous_3days": "Предыдущие 3 дня",
        "period_previous_week": "Предыдущая неделя",
        "period_previous_month": "Предыдущий месяц",

        "period_today": "Сегодня",
        "period_yesterday": "Вчера",
        "period_3days": "Последние 3 дня",
        "period_7days": "Последние 7 дней",
        "period_30days": "Последние 30 дней",
        "period_current_week": "Текущая неделя",
        "period_current_month": "Текущий месяц",

        "promo_not_found": "❌ Промокод не найден, неактивен или уже использован.",
        "promo_cancelled": "Ввод промокода отменён.",
        "promo_activated": (
            "✅ Промокод активирован.\n"
            "Тариф: {plan}\n"
            "Доступ открыт на {days} дней."
        ),

        "choose_access_option": "Выберите один из вариантов доступа:",
        "usdt_choose_plan": "Выберите тариф для оплаты через USDT TRC20:",
        "usdt_wallet_not_configured": "TRC20 кошелек не настроен в .env",
        "usdt_send_screenshot": "📸 Теперь отправь скрин перевода.",
        "usdt_choose_plan_first": "Сначала выбери тариф.",
        "usdt_screenshot_received": (
            "✅ Скрин получен.\n\n"
            "Теперь нажми кнопку 'Я оплатил'."
        ),
        "usdt_no_pending_payment": (
            "Не найдена активная заявка на оплату. Сначала выбери тариф."
        ),
        "usdt_payment_sent": (
            "✅ Заявка на проверку оплаты принята.\n\n"
            "После проверки ты получишь промокод от администратора."
        ),

        "stars_choose_plan": "Выберите тариф для оплаты через Telegram Stars:",
        "stars_plan_not_found": "Оплата получена, но тариф не найден.",
        "stars_payment_success_7days": "✅ Оплата успешна. Бот активен на 7 дней.",
        "stars_payment_success": (
            "✅ Оплата успешна.\n"
            "Тариф: {title}\n"
            "Доступ активирован на {days} дней."
        ),

        "bet_analysis_started": "🤖 Анализирую ставку.",
        "bet_saved": (
            "✅ Ставка распознана и сохранена\n\n"
            "🎯 Результат: {bet_result}\n"
            "📌 Тип ставки: {bet_type}\n"
            "💰 Сумма ставки: {stake_amount}\n"
            "📊 Коэффициент: {odds}\n\n"
            "📤 Можешь отправлять следующий скрин\n"
            "Осталось сегодня: {remaining}/{limit}"
        ),
        "bet_pending_saved": (
            "🕒 Ставка сохранена как нерассчитанная\n\n"
            "📌 Тип ставки: {bet_type}\n"
            "💰 Сумма ставки: {stake_amount}\n"
            "📊 Коэффициент: {odds}\n\n"
            "После расчета отправь финальный скрин этой ставки\n"
            "Осталось сегодня: {remaining}/{limit}"
        ),
        "bet_parse_failed": (
            "❌ Не удалось распознать ставку со скрина.\n"
            "Попробуй другой скрин или отправь более чёткий."
        ),

        "bet_result_win": "выигрыш",
        "bet_result_lose": "проигрыш",
        "bet_result_refund": "возврат",
        "bet_result_pending": "нерассчитанная",

        "trial_intro_push": (
            "🚀 Пробный доступ активирован!\n\n"
            "⚠️ У тебя есть 10 анализов в день\n\n"
            "📊 Что ты увидишь:\n"
            "• свой реальный ROI\n"
            "• где теряешь деньги\n"
            "• какие ставки работают лучше\n\n"
            "👇 Отправь первый скрин"
        ),
        "trial_after_first_push": (
            "📊 Первый результат уже есть.\n\n"
            "Даже 1 скрин уже показывает больше, чем большинство игроков видят за неделю.\n\n"
            "👉 Отправь ещё несколько ставок — соберём полную картину."
        ),
        "trial_after_third_push": (
            "📊 У тебя уже есть первые данные для выводов.\n\n"
            "❌ Большинство игроков даже не знают свой реальный ROI\n"
            "✅ Ты уже видишь то, что обычно скрыто\n\n"
            "🔥 Ещё немного — и картина по ставкам станет очевидной."
        ),
        "trial_limit_push": (
            "❌ Лимит достигнут ({used}/{limit})\n\n"
            "📊 Ты уже увидел базовую ценность бота.\n"
            "Представь, что будет, если отслеживать это каждый день.\n\n"
            "🔥 Открой полный доступ и масштабирй результат."
        ),
        "buy_access_push": (
            "🚀 Полный доступ даёт:\n\n"
            "📊 Полную статистику\n"
            "🧠 Глубокую аналитику\n"
            "📈 Контроль ROI и прибыли\n"
            "🔥 Выявление слабых мест\n\n"
            "👇 Выбери тариф"
        )
    },

    "en": {
        "start": "Hello 👋\nChoose an action:",
        "choose_lang": "Choose a language:",
        "language_changed": "✅ Language changed",

        "no_access": "⛔ You do not have active access.",
        "activate_access_first": "⛔ Activate access first via /start",
        "no_active_access_start": "⛔ You do not have active access. Press /start",

        "choose_period": "Choose a stats period:",
        "choose_full_stats_period": "Choose a period for full stats:",
        "choose_analytics_period": "Choose a period for analytics:",
        "enter_promo_hint": "Enter the promo code in one message:",

        "daily_limit_reached": (
            "⛔ Daily limit reached.\n\n"
            "Your plan allows {limit} screenshots per day.\n"
            "Try again tomorrow."
        ),

        "send_screen_with_limit": (
            "📤 Send a bet screenshot\n\n"
            "Today's limit: {limit}\n"
            "Used: {used}\n"
            "Remaining: {remaining}"
        ),

        "account_info": (
            "📈 Account info\n\n"
            "Plan: {plan}\n"
            "Access until: {access_until}\n\n"
            "Daily screenshot limit: {limit}\n"
            "Used today: {used}\n"
            "Remaining today: {remaining}"
        ),

        "stats_result": (
            "📊 My stats ({period})\n\n"
            "💰 Profit: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 Win rate: {win_rate}%\n"
            "📊 Avg odds: {avg_odds}\n\n"
            "🔥 Streak: {win_streak}"
        ),

        "full_stats_result": (
            "📈 Full stats ({period})\n\n"
            "💰 Profit: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 Win rate: {win_rate}%\n"
            "📊 Avg odds: {avg_odds}\n\n"
            "📦 Total bets: {total_bets}\n"
            "✅ Wins: {wins}\n"
            "❌ Losses: {losses}\n"
            "🔁 Refunds: {refunds}\n\n"
            "💵 Total stake: {total_stake}\n"
            "🔥 Current win streak: {win_streak}\n"
            "🏆 Best streak for the period: {best_win_streak}\n\n"
            "📌 Bet types:\n"
            "Total: {total_type_count}\n"
            "Result: {result_type_count}\n\n"
            "📊 By type:\n"
            "Total → {total_type_profit}\n"
            "Result → {result_type_profit}\n\n"
            "📈 By odds:\n"
            "<2 → {under_2_count} bets ({under_2_profit})\n"
            "≥2 → {over_2_count} bets ({over_2_profit})\n\n"
            "📉 Last 5 bets:\n"
            "{last_results}"
        ),

        "analytics_result": (
            "🧠 Analytics ({period})\n\n"
            "📊 Distribution:\n"
            "Total: {total_type_count}\n"
            "Result: {result_type_count}\n\n"
            "💵 Profit:\n"
            "Total → {total_type_profit}\n"
            "Result → {result_type_profit}\n\n"
            "📈 By odds:\n"
            "<2 → {under_2_count} bets ({under_2_profit})\n"
            "≥2 → {over_2_count} bets ({over_2_profit})\n\n"
            "🎯 Win rate:\n"
            "{win_rate}%\n\n"
            "🏆 Most effective:\n"
            "{best_type}\n\n"
            "⚠️ Weak spot:\n"
            "{worst_type}\n\n"
            "📌 Conclusion:\n"
            "{conclusion}\n\n"
            "{risk_block}\n"
            "{dynamics_block}\n\n"
            "🧠 Your style:\n"
            "{profile_title}\n\n"
            "📌 Profile:\n"
            "{profile_desc}"
        ),

        "bet_type_total": "Total",
        "bet_type_result": "Result",
        "bet_type_equal": "Equal",
        "bet_type_none": "No obvious weak spot",
        "market_type_1x2": "1X2",
        "market_type_total": "Total",
        "market_type_btts": "BTTS",
        "market_type_handicap": "Handicap",
        "market_type_double_chance": "1X/2X",
        "market_type_corners": "Corners",
        "market_type_cards": "Cards",
        "market_type_other": "Other",

        "conclusion_better_total": "You steadily profit from totals.",
        "conclusion_better_result": "Result bets work better for you.",
        "conclusion_equal": "Your bet types are balanced.",

        "conclusion_good": "You have good momentum and control.",
        "conclusion_neutral": "The result is stable, but there is room to grow.",
        "conclusion_bad": "Your results are dropping — review your strategy.",

        "coeff_under2": "Better to focus on odds below 2.",
        "coeff_over2": "Odds of 2 and above work better.",
        "coeff_under_2": "Odds below 2 work better.",
        "coeff_over_2": "Odds of 2 and above work better.",

        "risk_losing_streak": "⚠️ You have a losing streak ({streak}). It is recommended to reduce your stake size.",
        "risk_roi_drop": "⚠️ Profit in the last 3 days dropped compared with the previous 3 days.",
        "analytics_dynamics": "📈 Dynamics:\nLast 3 days: {recent_profit}\nPrevious 3 days: {previous_profit}",

        "profile_careful_title": "Careful player",
        "profile_careful_desc": "You more often choose odds below 2. This gives steadier but slower growth.",
        "profile_aggressive_title": "Aggressive player",
        "profile_aggressive_desc": "You often choose odds of 2 and above. This increases risk and makes results less stable.",
        "profile_balanced_title": "Balanced player",
        "profile_balanced_desc": "You use different odds quite evenly. The balance is good, but it is worth checking what really brings profit.",
        "profile_mixed_title": "Mixed style",
        "profile_mixed_desc": "You combine different approaches and odds.",
        "profile_system_title": "Systematic style",
        "profile_system_desc": "You stick to a stable and disciplined approach.",

        "full_stats_result_basic": "📈 Full stats ({period})\n\n💰 Final result\nProfit: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\nAvg odds: {avg_odds}\n\n📦 Activity\nTotal bets: {total_bets}\nSettled: {settled_bets}\nPending: {pending_bets}\n\n✅ Wins: {wins}\n❌ Losses: {losses}\n➖ Refunds: {refunds}\n\n💵 Total stake: {total_stake}\n💵 Settled stake: {settled_stake}\n\n🔥 Streaks\nCurrent win streak: {current_win_streak}\nBest win streak: {best_win_streak}\nWorst losing streak: {worst_lose_streak}\n\n🎯 By bet type\nTotals: {total_type_count} | {total_type_profit}\nResult: {result_type_count} | {result_type_profit}\n\n📈 By odds\n<2.0 : {odds_lt2_count} bets | {odds_lt2_profit}\n2.0–2.49 : {odds_mid_count} bets | {odds_mid_profit}\n2.5+ : {odds_high_count} bets | {odds_high_profit}\n\n🕓 Last 5 results\n{last_results}",
        "full_stats_result_vip": "📈 VIP Full stats ({period})\n\n💰 Final result\nProfit: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\nAvg odds: {avg_odds}\n\n📦 Activity\nTotal bets: {total_bets}\nSettled: {settled_bets}\nPending: {pending_bets}\n\n✅ Wins: {wins}\n❌ Losses: {losses}\n➖ Refunds: {refunds}\n\n💵 Total stake: {total_stake}\n💵 Settled stake: {settled_stake}\n\n🔥 Streaks\nCurrent win streak: {current_win_streak}\nBest win streak: {best_win_streak}\nWorst losing streak: {worst_lose_streak}\n\n🎯 By bet type\nTotals: {total_type_count} | profit {total_type_profit} | ROI {total_type_roi}%\nResult: {result_type_count} | profit {result_type_profit} | ROI {result_type_roi}%\n\n📈 By odds\n<2.0 : {odds_lt2_count} bets | {odds_lt2_profit} | ROI {odds_lt2_roi}%\n2.0–2.49 : {odds_mid_count} bets | {odds_mid_profit} | ROI {odds_mid_roi}%\n2.5+ : {odds_high_count} bets | {odds_high_profit} | ROI {odds_high_roi}%\n\n🕓 Last 5 results\n{last_results}",
        "analytics_result_basic": "🧠 Analytics ({period})\n\n📌 Overall rating\n{overall_title}\n{overall_desc}\n\n💰 Core numbers\nProfit: {net_profit}\nROI: {roi}%\nWin rate: {win_rate}%\n\n🏆 What works best\nBet type: {best_type}\nROI: {best_type_roi}%\n\nOdds: {best_odds_bucket}\nWin rate: {best_odds_win_rate}%\nROI: {best_odds_roi}%\n\n📉 What drags you down\n{weak_spot_text}\n\n📈 Momentum\n{dynamics_text}\n{trend_text}\n\n🧠 Player profile\n{profile_title}\n\n{profile_desc}\n\n⚠️ Attention\n{risk_block}\n\n{vip_teaser}",
        "analytics_result_vip": "🧠 VIP Analytics ({period})\n\n📌 Overall summary\n{overall_title}\n{overall_desc}\n💰 Profit: {net_profit}\n📈 ROI: {roi}%\n🎯 Win rate: {win_rate}%\n📦 Settled bets: {settled_bets}\n\n📊 By bet type\n{total_breakdown}\n{result_breakdown}\n\n📈 By odds\n{odds_lt2_breakdown}\n{odds_mid_breakdown}\n{odds_high_breakdown}\n\n📉 Stability\n{stability_block}\n\n📈 Momentum\n{dynamics_text}\n\n🧠 Profile\n{profile_title}\n{profile_desc}\n\n✅ Strengths\n{strengths_block}\n\n⚠️ Weak spots\n{weak_spot_text}\n\n🚨 Risks\n{risk_block}\n\n📌 Recommendation\n{recommendation_text}",
        "analytics_odds_bucket_lt2": "<2.0",
        "analytics_odds_bucket_mid": "2.0–2.49",
        "analytics_odds_bucket_high": "2.5+",
        "analytics_odds_bucket_none": "Not enough data",
        "analytics_status_great_title": "Result: very strong",
        "analytics_status_great_desc": "You are in profit and showing strong momentum.",
        "analytics_status_good_title": "Result: good",
        "analytics_status_good_desc": "You are playing steadily and controlling the distance.",
        "analytics_status_neutral_title": "Result: neutral",
        "analytics_status_neutral_desc": "There is already a base, but the quality of play can improve.",
        "analytics_status_bad_title": "Result: weak",
        "analytics_status_bad_desc": "Right now the analytics shows where you should reduce risk.",
        "analytics_compare_block": "{current_label}: {current_profit} | ROI {current_roi}% | WR {current_wr}%\n{previous_label}: {previous_profit} | ROI {previous_roi}% | WR {previous_wr}%",
        "analytics_type_breakdown_line": "{label} → {count} bets | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_odds_breakdown_line": "{bucket} → {count} bets | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_market_breakdown_line": "{label} → {count} bets | WR {win_rate}% | ROI {roi}% | Profit {profit}",
        "analytics_no_market_data": "Not enough data by bet type.",
        "analytics_weak_market_line": "Market type: {label} | ROI {roi}% | Profit {profit}",
        "analytics_strength_market": "— strong market: {label}",
        "analytics_stability_block": "Current win streak: {current_win_streak}\nBest win streak: {best_win_streak}\nWorst losing streak: {worst_lose_streak}",
        "analytics_weak_type_line": "Bet type: {label} | ROI {roi}% | Profit {profit}",
        "analytics_weak_odds_line": "Odds: {label} | ROI {roi}% | Profit {profit}",
        "analytics_no_weak_spot": "No clear weak spot yet.",
        "analytics_strength_type": "— strongest bet type: {label}",
        "analytics_strength_odds": "— strongest odds segment: {label}",
        "analytics_no_strengths": "There is not enough data yet for strong conclusions.",
        "analytics_trend_up": "Your form is improving 📈",
        "analytics_trend_down": "The latest segment is weaker than the previous one 📉",
        "analytics_trend_flat": "Momentum is close to stable ➖",
        "analytics_risk_losing_streak": "— there was a losing streak: {streak}",
        "analytics_risk_negative_roi": "— overall ROI moved into a noticeable minus",
        "analytics_risk_high_odds_drag": "— odds of 2.5+ are dragging the result down",
        "analytics_risk_low_winrate": "— win rate is below a safer level",
        "analytics_risk_downtrend": "— the latest segment is worse than the previous one",
        "analytics_no_risks": "No major risks were detected for the selected period.",
        "analytics_recommendation_cut_high_odds": "Reduce the share of 2.5+ odds and focus on more stable segments.",
        "analytics_recommendation_focus_total": "For now it is better to shift focus toward totals — they bring a better result.",
        "analytics_recommendation_focus_result": "Result bets are working better right now — it makes sense to reinforce that direction.",
        "analytics_recommendation_reduce_risk": "During losing streaks reduce risk and do not increase aggression.",
        "analytics_recommendation_keep_discipline": "Keep your current discipline and watch which segment holds ROI higher.",
        "analytics_vip_teaser": "🔓 VIP includes:\n• ROI for each bet type\n• Extended momentum\n• Personal recommendations\n• Deep style analysis",
        "period_recent_3days": "Last 3 days",
        "period_previous_3days": "Previous 3 days",
        "period_previous_week": "Previous week",
        "period_previous_month": "Previous month",

        "period_today": "Today",
        "period_yesterday": "Yesterday",
        "period_3days": "Last 3 days",
        "period_7days": "Last 7 days",
        "period_30days": "Last 30 days",
        "period_current_week": "Current week",
        "period_current_month": "Current month",

        "promo_not_found": "❌ Promo code not found, inactive, or already used.",
        "promo_cancelled": "Promo code entry cancelled.",
        "promo_activated": (
            "✅ Promo code activated.\n"
            "Plan: {plan}\n"
            "Access opened for {days} days."
        ),

        "choose_access_option": "Choose one of the access options:",
        "usdt_choose_plan": "Choose a plan for USDT TRC20 payment:",
        "usdt_wallet_not_configured": "TRC20 wallet is not configured in .env",
        "usdt_send_screenshot": "📸 Now send a payment screenshot.",
        "usdt_choose_plan_first": "Choose a plan first.",
        "usdt_screenshot_received": (
            "✅ Screenshot received.\n\n"
            "Now press the 'I paid' button."
        ),
        "usdt_no_pending_payment": (
            "No active payment request found. Choose a plan first."
        ),
        "usdt_payment_sent": (
            "✅ Payment verification request accepted.\n\n"
            "After verification you will receive a promo code from the admin."
        ),

        "stars_choose_plan": "Choose a plan for Telegram Stars payment:",
        "stars_plan_not_found": "Payment received, but the plan was not found.",
        "stars_payment_success_7days": "✅ Payment successful. Bot is active for 7 days.",
        "stars_payment_success": (
            "✅ Payment successful.\n"
            "Plan: {title}\n"
            "Access activated for {days} days."
        ),

        "bet_analysis_started": "🤖 Analyzing your bet.",
        "bet_saved": (
            "✅ Bet recognized and saved\n\n"
            "🎯 Result: {bet_result}\n"
            "📌 Bet type: {bet_type}\n"
            "💰 Stake amount: {stake_amount}\n"
            "📊 Odds: {odds}\n\n"
            "📤 You can send the next screenshot\n"
            "Remaining today: {remaining}/{limit}"
        ),
        "bet_pending_saved": (
            "🕒 Bet saved as unsettled\n\n"
            "📌 Bet type: {bet_type}\n"
            "💰 Stake amount: {stake_amount}\n"
            "📊 Odds: {odds}\n\n"
            "After settlement, send the final screenshot of this bet\n"
            "Remaining today: {remaining}/{limit}"
        ),
        "bet_parse_failed": (
            "❌ Failed to recognize the bet from the screenshot.\n"
            "Try another screenshot or send a clearer one."
        ),

        "bet_result_win": "win",
        "bet_result_lose": "loss",
        "bet_result_refund": "refund",
        "bet_result_pending": "unsettled",

        "trial_intro_push": (
            "🚀 Trial access activated!\n\n"
            "⚠️ You have 10 analyses per day\n\n"
            "📊 What you will see:\n"
            "• your real ROI\n"
            "• where you are losing money\n"
            "• which bets work better\n\n"
            "👇 Send your first screenshot"
        ),
        "trial_after_first_push": (
            "📊 You already have your first result.\n\n"
            "Even 1 screenshot already shows more than most players see in a week.\n\n"
            "👉 Send a few more bets — let’s build the full picture."
        ),
        "trial_after_third_push": (
            "📊 You already have the first data for conclusions.\n\n"
            "❌ Most players do not even know their real ROI\n"
            "✅ You already see what is usually hidden\n\n"
            "🔥 A little more — and the full betting picture will become obvious."
        ),
        "trial_limit_push": (
            "❌ Limit reached ({used}/{limit})\n\n"
            "📊 You have already seen the basic value of the bot.\n"
            "Imagine what happens if you track this every day.\n\n"
            "🔥 Unlock full access and scale your result."
        ),
        "buy_access_push": (
            "🚀 Full access gives you:\n\n"
            "📊 Full statistics\n"
            "🧠 Deep analytics\n"
            "📈 ROI and profit control\n"
            "🔥 Identification of weak spots\n\n"
            "👇 Choose a plan"
        )
    }
}


def get_text(lang: str, key: str) -> str:
    safe_lang = (lang or "en").lower()

    if safe_lang.startswith("uk") or safe_lang.startswith("ua"):
        code = "ua"
    elif safe_lang.startswith("ru"):
        code = "ru"
    else:
        code = "en"

    return TEXTS.get(code, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
