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
