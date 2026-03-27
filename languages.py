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
            "🎯 Виграш: {win_rate}%\n"
            "📊 Середній коеф: {avg_odds}\n\n"
            "🔥 Серія: {win_streak}"
        ),

        "full_stats_result": (
            "📈 Повна статистика ({period})\n\n"
            "💰 Прибуток: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 Виграш: {win_rate}%\n"
            "📊 Середній коеф: {avg_odds}\n\n"
            "📦 Всього ставок: {total_bets}\n"
            "✅ Виграшних: {wins}\n"
            "❌ Програшних: {losses}\n"
            "🔁 Повернень: {refunds}\n\n"
            "💵 Сума ставок: {total_stake}\n"
            "🔥 Поточна серія перемог: {win_streak}\n"
            "🏆 Найкраща серія за період: {best_win_streak}\n\n"
            "📌 Типи ставок:\n"
            "Тотал: {total_type_count}\n"
            "Результат: {result_type_count}\n\n"
            "📊 По типах:\n"
            "Тотал → {total_type_profit}\n"
            "Результат → {result_type_profit}\n\n"
            "📈 По коефіцієнтах:\n"
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

        "bet_analysis_started": "🤖 Аналізую ставку...",
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
            "🎯 Выигрыш: {win_rate}%\n"
            "📊 Средний коэфф: {avg_odds}\n\n"
            "🔥 Серия: {win_streak}"
        ),

        "full_stats_result": (
            "📈 Полная статистика ({period})\n\n"
            "💰 Прибыль: {net_profit}\n"
            "📈 ROI: {roi}%\n"
            "🎯 Выигрыш: {win_rate}%\n"
            "📊 Средний коэфф: {avg_odds}\n\n"
            "📦 Всего ставок: {total_bets}\n"
            "✅ Выигрышных: {wins}\n"
            "❌ Проигрышных: {losses}\n"
            "🔁 Возвратов: {refunds}\n\n"
            "💵 Сумма ставок: {total_stake}\n"
            "🔥 Текущая серия побед: {win_streak}\n"
            "🏆 Лучшая серия за период: {best_win_streak}\n\n"
            "📌 Типы ставок:\n"
            "Тотал: {total_type_count}\n"
            "Результат: {result_type_count}\n\n"
            "📊 По типам:\n"
            "Тотал → {total_type_profit}\n"
            "Результат → {result_type_profit}\n\n"
            "📈 По коэффициентам:\n"
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

        "bet_analysis_started": "🤖 Анализирую ставку...",
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
    }
}


def get_text(lang: str, key: str) -> str:
    safe_lang = "ru" if lang == "ru" else "ua"
    return TEXTS.get(safe_lang, TEXTS["ua"]).get(key, TEXTS["ua"].get(key, key))
