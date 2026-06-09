const TRANSLATIONS = {
  en: {
    pageTitle: "CADR Control Room",
    heroEyebrow: "CADR Control Room",
    heroTitle: "Cross-asset monitoring built for decision-making, not raw dumps.",
    heroCopy:
      "Watch divergence pressure, signal quality, and market regime in one screen. Keep the payload available on demand, but let the interface surface what matters first.",
    actionsTitle: "Actions",
    refreshDashboard: "Refresh Dashboard",
    runDailyOverview: "Run Daily Overview",
    runPairScan: "Run Pair Scan",
    baseAsset: "Base asset",
    quoteAsset: "Quote asset",
    lookbackDays: "Lookback days",
    runCustomPair: "Run Custom Pair",
    actionLogIdle: "Dashboard is waiting for the next action.",
    busyTitle: "Research is running",
    busySubtitle: "Your click worked. CADR is now querying data and building the result.",
    systemSnapshotTitle: "System Snapshot",
    systemSnapshotCaption: "High-level health, cadence, and latest system outputs.",
    latestDailyOverviewTitle: "Latest Daily Overview",
    latestScanTitle: "Latest Scan",
    signalBoardTitle: "Signal Board",
    signalBoardCaption: "Best opportunities and biggest dislocations ranked visually.",
    pairMonitorTitle: "Pair Monitor",
    pairMonitorCaption: "Click a pair to inspect history, reasoning, and strategy state.",
    pairDetailTitle: "Pair Detail",
    pairDetailCaption: "Expanded view with signal summary, trend context, and optional raw payload.",
    recentRunsTitle: "Recent Runs",
    recentRunsCaption: "Operational log of scans, overview pulls, and pair-specific jobs.",
    watchlistTitle: "Watchlist Monitor",
    watchlistCaption:
      "Edit the default pair set, keep the background monitor running, and save entry checkpoints for next-day validation.",
    backgroundMonitor: "Background monitor",
    intervalMinutes: "Interval, minutes",
    monitorLookbackDays: "Lookback days",
    watchlistEditorLabel: "Pairs, one per line",
    saveWatchlist: "Save watchlist",
    runMonitorNow: "Run monitor now",
    saveSnapshot: "Save snapshot",
    evaluateSnapshot: "Evaluate snapshot",
    evaluateForecasts: "Evaluate forecasts",
    forecastSummaryTitle: "Forecast Summary",
    recentForecastsTitle: "Recent Forecasts",
    snapshotSummaryTitle: "Snapshot Status",
    snapshotEvaluationTitle: "Snapshot Evaluation",
    forecastSummaryEmpty: "No forecast checkpoints have been saved yet.",
    watchlistStatusIdle: "Watchlist settings will appear here.",
    snapshotStatusIdle: "Snapshot tools are ready.",
    monitorEnabledYes: "Enabled",
    monitorEnabledNo: "Disabled",
    monitorNextRun: "Next run",
    monitorLastRun: "Last run",
    forecastPending: "Pending",
    forecastEvaluated: "Evaluated",
    forecastWins: "Wins",
    forecastLosses: "Losses",
    forecastFlat: "Flat",
    exportPath: "Export file",
    entryCheckpoint: "Entry checkpoint",
    dueAt: "Due",
    outcome: "Outcome",
    noForecasts: "No forecast checkpoints yet.",
    noSnapshotYet: "No snapshot has been saved yet.",
    noSnapshotEvaluationYet: "No snapshot evaluation has been run yet.",
    snapshotGeneratedAt: "Snapshot generated",
    snapshotPath: "Snapshot file",
    snapshotPairs: "Pairs in snapshot",
    evaluationAt: "Evaluation time",
    evaluationFile: "Evaluation file",
    skipped: "skipped",
    saveWatchlistAction: "Save watchlist",
    runMonitorAction: "Run monitor",
    saveSnapshotAction: "Save snapshot",
    evaluateSnapshotAction: "Evaluate snapshot",
    evaluateForecastsAction: "Evaluate forecasts",
    watchlistSaved: "Watchlist updated successfully.",
    snapshotSaved: "Snapshot saved successfully.",
    snapshotEvaluatedMessage: "Snapshot evaluated: {count} pairs processed.",
    forecastsEvaluated: "{count} forecasts evaluated.",
    pendingOutcome: "Pending",
    evaluatedOutcome: "Evaluated",
    win: "Win",
    loss: "Loss",
    flat: "Flat",
    languageLabel: "Language",
    autoLanguage: "Auto (browser/system)",
    pair: "Pair",
    status: "Status",
    direction: "Direction",
    zScore: "Z-Score",
    conviction: "Conviction",
    divergence: "Divergence",
    correlation: "Correlation",
    regime: "Regime",
    monitoredPairs: "Monitored Pairs",
    latestSignals: "Latest Signals",
    healthySignals: "Healthy Signals",
    signalFailures: "Signal Failures",
    monitoredPairsNote: "Pairs configured for the default scan set.",
    latestSignalsNote: "Pairs that currently have a stored signal snapshot.",
    healthySignalsNote: "Signals generated without execution or data errors.",
    signalFailuresNote: "Pairs that need a retry, data fix, or better fallbacks.",
    noDailyOverview: "No daily overview has been run yet.",
    noPairScan: "No pair scan has been run yet.",
    statusLabel: "Status",
    windowLabel: "Window",
    messageLabel: "Message",
    signalLabel: "Signal",
    noMessage: "No message",
    noAdditionalSummary: "No additional summary available.",
    defaultScanSignalSummary: "{ok} ok / {error} errors across {total} pairs.",
    runScanToPopulate: "Run a scan to populate the signal board.",
    dislocation: "Dislocation",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "No runs have been recorded yet.",
    unknownPair: "Unknown pair",
    pairContextLine: "{direction} with {divergence} context.",
    returnSpread: "Return Spread",
    baseVsPeer: "Base vs Peer",
    operatorNotes: "Operator Notes",
    summary: "Summary",
    decision: "Decision",
    riskNotes: "Risk Notes",
    noSummary: "No summary available yet.",
    noDecision: "No decision text available.",
    noRiskNotes: "No explicit risk notes returned.",
    zScoreTrend: "Z-Score Trend",
    savedObservations: "Last {count} saved observations",
    correlationTrend: "Correlation Trend",
    pairStability: "Stability of the pair relationship",
    recentHistory: "Recent History",
    recentSignalSnapshots: "Most recent signal snapshots",
    noHistoryEntries: "No history entries yet.",
    noHistoryYet: "Not enough history yet.",
    needTwoObservations: "Need at least 2 saved observations to draw a trend.",
    rawStrategyPayload: "Raw Strategy Payload",
    rawPayloadCaption: "Available when needed for debugging, audit, or export.",
    showJson: "Show JSON",
    hideJson: "Hide JSON",
    noPairDetailYet: "Run a pair scan to unlock detailed history, trend charts, and operator notes.",
    actionRunning: "{label} is running...",
    actionSuccess: "{label} finished successfully.",
    actionFailed: "{label} failed: {error}",
    refreshAction: "Refresh",
    dailyOverviewAction: "Daily overview",
    defaultScanAction: "Default scan",
    pairScanAction: "Pair scan {pair}",
    initialLoadFailed: "Initial load failed: {error}",
    ready: "ready",
    loading: "loading",
    running: "running",
    pending: "pending",
    evaluated: "evaluated",
    unknown: "unknown",
    ok: "ok",
    error: "error",
    partial: "partial",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Daily overview",
    defaultScanRunType: "Default scan",
    pairScanRunType: "Pair scan",
    baseOutperforming: "Base outperforming",
    baseLagging: "Base lagging",
    broadlyTracking: "Broadly tracking",
    crisis: "Crisis",
    riskOn: "Risk on",
    riskOff: "Risk off",
    zScoreHelp:
      "How far the pair has drifted from its usual relationship. Bigger values mean a stronger divergence and a more interesting mean-reversion setup.",
    convictionHelp:
      "Overall confidence in the signal. Higher values mean more supporting evidence across market regime, relative performance, and technical context.",
    correlationHelp:
      "How tightly the two assets usually move together. Higher values mean the pair is structurally more suitable for divergence and mean-reversion analysis.",
  },
  ru: {
    pageTitle: "CADR Control Room",
    heroEyebrow: "CADR Control Room",
    heroTitle: "Мониторинг кросс-активов для решений, а не для просмотра сырых дампов.",
    heroCopy:
      "Следи за силой расхождения, качеством сигнала и рыночным режимом в одном экране. Сырой payload остаётся доступным по запросу, но интерфейс сначала показывает главное.",
    actionsTitle: "Действия",
    refreshDashboard: "Обновить дашборд",
    runDailyOverview: "Запустить обзор рынка",
    runPairScan: "Запустить скан пар",
    baseAsset: "Базовый актив",
    quoteAsset: "Сравниваемый актив",
    lookbackDays: "Период, дней",
    runCustomPair: "Запустить свою пару",
    actionLogIdle: "Дашборд ждёт следующего действия.",
    busyTitle: "Поиск и ресёрч выполняются",
    busySubtitle: "Клик сработал. CADR уже запрашивает данные и собирает результат.",
    systemSnapshotTitle: "Снимок системы",
    systemSnapshotCaption: "Верхнеуровневое состояние, ритм запусков и последние результаты системы.",
    latestDailyOverviewTitle: "Последний обзор рынка",
    latestScanTitle: "Последний скан",
    signalBoardTitle: "Доска сигналов",
    signalBoardCaption: "Лучшие возможности и самые сильные расхождения, отсортированные визуально.",
    pairMonitorTitle: "Монитор пар",
    pairMonitorCaption: "Нажми на пару, чтобы посмотреть историю, аргументацию и состояние стратегии.",
    pairDetailTitle: "Детали пары",
    pairDetailCaption: "Расширенный вид с сигналом, контекстом тренда и сырым payload по запросу.",
    recentRunsTitle: "Последние запуски",
    recentRunsCaption: "Операционный журнал сканов, обзоров и точечных запусков по парам.",
    watchlistTitle: "Watchlist и мониторинг",
    watchlistCaption:
      "Редактируй набор пар по умолчанию, держи фоновый монитор активным и сохраняй точки входа для проверки прогноза на следующий день.",
    backgroundMonitor: "Фоновый монитор",
    intervalMinutes: "Интервал, минут",
    monitorLookbackDays: "Период, дней",
    watchlistEditorLabel: "Пары, по одной на строку",
    saveWatchlist: "Сохранить watchlist",
    runMonitorNow: "Запустить монитор сейчас",
    saveSnapshot: "Сохранить snapshot",
    evaluateSnapshot: "Проверить snapshot",
    evaluateForecasts: "Проверить прогнозы",
    forecastSummaryTitle: "Сводка прогнозов",
    recentForecastsTitle: "Последние прогнозы",
    snapshotSummaryTitle: "Статус snapshot",
    snapshotEvaluationTitle: "Проверка snapshot",
    forecastSummaryEmpty: "Точки входа пока не сохранены.",
    watchlistStatusIdle: "Здесь появятся настройки watchlist.",
    snapshotStatusIdle: "Инструменты snapshot готовы.",
    monitorEnabledYes: "Включён",
    monitorEnabledNo: "Выключен",
    monitorNextRun: "Следующий запуск",
    monitorLastRun: "Последний запуск",
    forecastPending: "В ожидании",
    forecastEvaluated: "Проверено",
    forecastWins: "Удачные",
    forecastLosses: "Неудачные",
    forecastFlat: "Нейтральные",
    exportPath: "Файл экспорта",
    entryCheckpoint: "Точка входа",
    dueAt: "Проверка",
    outcome: "Итог",
    noForecasts: "Сохранённых точек входа пока нет.",
    noSnapshotYet: "Snapshot ещё не сохранён.",
    noSnapshotEvaluationYet: "Проверка snapshot ещё не запускалась.",
    snapshotGeneratedAt: "Snapshot создан",
    snapshotPath: "Файл snapshot",
    snapshotPairs: "Пар в snapshot",
    evaluationAt: "Время проверки",
    evaluationFile: "Файл проверки",
    skipped: "пропущено",
    saveWatchlistAction: "Сохранение watchlist",
    runMonitorAction: "Запуск монитора",
    saveSnapshotAction: "Сохранение snapshot",
    evaluateSnapshotAction: "Проверка snapshot",
    evaluateForecastsAction: "Проверка прогнозов",
    watchlistSaved: "Watchlist успешно обновлён.",
    snapshotSaved: "Snapshot успешно сохранён.",
    snapshotEvaluatedMessage: "Snapshot проверен: обработано пар {count}.",
    forecastsEvaluated: "Проверено прогнозов: {count}.",
    pendingOutcome: "В ожидании",
    evaluatedOutcome: "Проверено",
    win: "Успех",
    loss: "Ошибка",
    flat: "Нейтрально",
    languageLabel: "Язык",
    autoLanguage: "Авто (браузер/система)",
    pair: "Пара",
    status: "Статус",
    direction: "Направление",
    zScore: "Z-Score",
    conviction: "Уверенность",
    divergence: "Расхождение",
    correlation: "Корреляция",
    regime: "Режим",
    monitoredPairs: "Отслеживаемые пары",
    latestSignals: "Актуальные сигналы",
    healthySignals: "Успешные сигналы",
    signalFailures: "Ошибки сигналов",
    monitoredPairsNote: "Пары, включённые в стандартный набор сканирования.",
    latestSignalsNote: "Пары, по которым уже сохранён актуальный снимок сигнала.",
    healthySignalsNote: "Сигналы, полученные без ошибок выполнения или данных.",
    signalFailuresNote: "Пары, которым нужен повторный запуск, исправление данных или лучший fallback.",
    noDailyOverview: "Обзор рынка ещё не запускался.",
    noPairScan: "Скан пар ещё не запускался.",
    statusLabel: "Статус",
    windowLabel: "Интервал",
    messageLabel: "Сообщение",
    signalLabel: "Сигнал",
    noMessage: "Нет сообщения",
    noAdditionalSummary: "Дополнительной сводки пока нет.",
    defaultScanSignalSummary: "{ok} ok / {error} ошибок по {total} парам.",
    runScanToPopulate: "Запусти сканирование, чтобы заполнить доску сигналов.",
    dislocation: "Отклонение",
    longLabel: "Лонг {asset}",
    shortLabel: "Шорт {asset}",
    noRuns: "Запусков пока нет.",
    unknownPair: "Неизвестная пара",
    pairContextLine: "{direction} при контексте {divergence}.",
    returnSpread: "Спред доходности",
    baseVsPeer: "База против пары",
    operatorNotes: "Заметки оператора",
    summary: "Сводка",
    decision: "Решение",
    riskNotes: "Риски",
    noSummary: "Сводка пока недоступна.",
    noDecision: "Текст решения пока недоступен.",
    noRiskNotes: "Явные риск-заметки не были возвращены.",
    zScoreTrend: "Тренд Z-Score",
    savedObservations: "Последние сохранённые наблюдения: {count}",
    correlationTrend: "Тренд корреляции",
    pairStability: "Насколько стабильна связь между активами",
    recentHistory: "Последняя история",
    recentSignalSnapshots: "Самые свежие снимки сигнала",
    noHistoryEntries: "Истории пока нет.",
    noHistoryYet: "Истории пока недостаточно.",
    needTwoObservations: "Нужно минимум 2 сохранённых наблюдения, чтобы построить тренд.",
    rawStrategyPayload: "Сырой payload стратегии",
    rawPayloadCaption: "Доступен по запросу для отладки, аудита или экспорта.",
    showJson: "Показать JSON",
    hideJson: "Скрыть JSON",
    noPairDetailYet: "Запусти скан пары, чтобы открыть историю, графики и заметки оператора.",
    actionRunning: "{label} выполняется...",
    actionSuccess: "{label} успешно завершён.",
    actionFailed: "{label} завершился ошибкой: {error}",
    refreshAction: "Обновление",
    dailyOverviewAction: "Обзор рынка",
    defaultScanAction: "Скан по умолчанию",
    pairScanAction: "Скан пары {pair}",
    initialLoadFailed: "Начальная загрузка не удалась: {error}",
    ready: "готово",
    loading: "загрузка",
    running: "выполняется",
    pending: "в ожидании",
    evaluated: "проверено",
    skipped: "пропущено",
    unknown: "неизвестно",
    ok: "ok",
    error: "ошибка",
    partial: "частично",
    longWord: "Лонг",
    shortWord: "Шорт",
    dailyOverviewRunType: "Обзор рынка",
    defaultScanRunType: "Скан по умолчанию",
    pairScanRunType: "Скан пары",
    baseOutperforming: "База сильнее рынка",
    baseLagging: "База отстаёт",
    broadlyTracking: "Движение в целом синхронно",
    crisis: "Кризис",
    riskOn: "Склонность к риску",
    riskOff: "Уход от риска",
    zScoreHelp:
      "Показывает, насколько пара ушла от своей обычной связи. Чем больше значение, тем сильнее перекос и тем интереснее идея на возврат к среднему.",
    convictionHelp:
      "Итоговая уверенность в сигнале. Чем выше значение, тем больше подтверждений со стороны режима рынка, относительной динамики и технического контекста.",
    correlationHelp:
      "Показывает, насколько эти два актива обычно двигаются вместе. Чем выше значение, тем лучше пара подходит для анализа расхождений и возврата к среднему.",
  },
  de: {
    pageTitle: "CADR Leitstand",
    heroEyebrow: "CADR Leitstand",
    heroTitle: "Cross-Asset-Monitoring für Entscheidungen statt roher Datenblöcke.",
    heroCopy:
      "Beobachte Divergenzdruck, Signalqualität und Marktregime auf einem Bildschirm. Die Rohdaten bleiben bei Bedarf verfügbar, aber die Oberfläche zeigt zuerst das Wesentliche.",
    actionsTitle: "Aktionen",
    refreshDashboard: "Dashboard aktualisieren",
    runDailyOverview: "Tagesüberblick starten",
    runPairScan: "Paar-Scan starten",
    baseAsset: "Basis-Asset",
    quoteAsset: "Vergleichs-Asset",
    lookbackDays: "Rückblick in Tagen",
    runCustomPair: "Eigenes Paar starten",
    actionLogIdle: "Das Dashboard wartet auf die nächste Aktion.",
    systemSnapshotTitle: "Systemübersicht",
    systemSnapshotCaption: "Gesundheit, Taktung und letzte Systemausgaben auf hoher Ebene.",
    latestDailyOverviewTitle: "Letzter Tagesüberblick",
    latestScanTitle: "Letzter Scan",
    signalBoardTitle: "Signal-Board",
    signalBoardCaption: "Die besten Chancen und stärksten Abweichungen visuell sortiert.",
    pairMonitorTitle: "Paar-Monitor",
    pairMonitorCaption: "Klicke auf ein Paar, um Verlauf, Begründung und Strategiestatus zu sehen.",
    pairDetailTitle: "Paar-Details",
    pairDetailCaption: "Erweiterte Ansicht mit Signalzusammenfassung, Trendkontext und optionalem Roh-Payload.",
    recentRunsTitle: "Letzte Läufe",
    recentRunsCaption: "Operatives Protokoll von Scans, Übersichten und paarbezogenen Jobs.",
    pair: "Paar",
    status: "Status",
    direction: "Richtung",
    zScore: "Z-Score",
    conviction: "Überzeugung",
    divergence: "Divergenz",
    correlation: "Korrelation",
    regime: "Regime",
    monitoredPairs: "Überwachte Paare",
    latestSignals: "Neueste Signale",
    healthySignals: "Saubere Signale",
    signalFailures: "Signalfehler",
    monitoredPairsNote: "Paare im Standard-Scan-Set.",
    latestSignalsNote: "Paare mit gespeichertem aktuellem Signalsnapshot.",
    healthySignalsNote: "Signale ohne Ausführungs- oder Datenfehler.",
    signalFailuresNote: "Paare mit Bedarf für Retry, Datenfix oder besseren Fallback.",
    noDailyOverview: "Noch kein Tagesüberblick ausgeführt.",
    noPairScan: "Noch kein Paar-Scan ausgeführt.",
    statusLabel: "Status",
    windowLabel: "Zeitraum",
    messageLabel: "Meldung",
    signalLabel: "Signal",
    noMessage: "Keine Meldung",
    noAdditionalSummary: "Keine zusätzliche Zusammenfassung verfügbar.",
    defaultScanSignalSummary: "{ok} ok / {error} Fehler über {total} Paare.",
    runScanToPopulate: "Starte einen Scan, um das Signal-Board zu füllen.",
    dislocation: "Abweichung",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Noch keine Läufe aufgezeichnet.",
    unknownPair: "Unbekanntes Paar",
    pairContextLine: "{direction} mit Kontext {divergence}.",
    returnSpread: "Renditespread",
    baseVsPeer: "Basis vs. Peer",
    operatorNotes: "Operator-Hinweise",
    summary: "Zusammenfassung",
    decision: "Entscheidung",
    riskNotes: "Risikohinweise",
    noSummary: "Noch keine Zusammenfassung verfügbar.",
    noDecision: "Noch kein Entscheidungstext verfügbar.",
    noRiskNotes: "Keine expliziten Risikohinweise zurückgegeben.",
    zScoreTrend: "Z-Score-Trend",
    savedObservations: "Letzte gespeicherte Beobachtungen: {count}",
    correlationTrend: "Korrelationstrend",
    pairStability: "Stabilität der Paarbeziehung",
    recentHistory: "Jüngste Historie",
    recentSignalSnapshots: "Neueste Signalsnapshots",
    noHistoryEntries: "Noch keine Historie vorhanden.",
    noHistoryYet: "Noch nicht genug Historie.",
    needTwoObservations: "Mindestens 2 gespeicherte Beobachtungen nötig, um einen Trend zu zeichnen.",
    rawStrategyPayload: "Rohes Strategie-Payload",
    rawPayloadCaption: "Bei Bedarf für Debugging, Audit oder Export verfügbar.",
    showJson: "JSON anzeigen",
    hideJson: "JSON ausblenden",
    noPairDetailYet: "Führe einen Paar-Scan aus, um Historie, Trendgrafiken und Operator-Hinweise zu sehen.",
    actionRunning: "{label} läuft...",
    actionSuccess: "{label} erfolgreich abgeschlossen.",
    actionFailed: "{label} fehlgeschlagen: {error}",
    refreshAction: "Aktualisierung",
    dailyOverviewAction: "Tagesüberblick",
    defaultScanAction: "Standard-Scan",
    pairScanAction: "Paar-Scan {pair}",
    initialLoadFailed: "Erstladung fehlgeschlagen: {error}",
    ready: "bereit",
    loading: "lädt",
    running: "läuft",
    unknown: "unbekannt",
    ok: "ok",
    error: "fehler",
    partial: "teilweise",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Tagesüberblick",
    defaultScanRunType: "Standard-Scan",
    pairScanRunType: "Paar-Scan",
    baseOutperforming: "Basis performt besser",
    baseLagging: "Basis hinkt hinterher",
    broadlyTracking: "Läuft weitgehend gemeinsam",
    crisis: "Krise",
    riskOn: "Risk-on",
    riskOff: "Risk-off",
    zScoreHelp:
      "Zeigt, wie weit sich das Paar von seiner üblichen Beziehung entfernt hat. Höhere Werte bedeuten eine stärkere Divergenz und ein interessanteres Mean-Reversion-Setup.",
    convictionHelp:
      "Gesamtvertrauen in das Signal. Höhere Werte bedeuten mehr Bestätigung durch Marktregime, relative Performance und technischen Kontext.",
    correlationHelp:
      "Zeigt, wie eng sich die beiden Assets normalerweise gemeinsam bewegen. Höhere Werte bedeuten, dass das Paar strukturell besser für Divergenz- und Mean-Reversion-Analysen geeignet ist.",
  },
  fr: {
    pageTitle: "Centre de contrôle CADR",
    heroEyebrow: "Centre de contrôle CADR",
    heroTitle: "Un suivi cross-asset pensé pour la décision, pas pour des dumps JSON bruts.",
    heroCopy:
      "Surveille la pression de divergence, la qualité du signal et le régime de marché sur un seul écran. Le payload brut reste disponible à la demande, mais l’interface met d’abord l’essentiel en avant.",
    actionsTitle: "Actions",
    refreshDashboard: "Rafraîchir le tableau",
    runDailyOverview: "Lancer la vue marché",
    runPairScan: "Lancer le scan de paires",
    baseAsset: "Actif de base",
    quoteAsset: "Actif comparé",
    lookbackDays: "Fenêtre en jours",
    runCustomPair: "Lancer une paire personnalisée",
    actionLogIdle: "Le tableau attend la prochaine action.",
    systemSnapshotTitle: "Vue système",
    systemSnapshotCaption: "Santé globale, cadence et dernières sorties du système.",
    latestDailyOverviewTitle: "Dernière vue marché",
    latestScanTitle: "Dernier scan",
    signalBoardTitle: "Tableau des signaux",
    signalBoardCaption: "Les meilleures opportunités et les plus fortes divergences, classées visuellement.",
    pairMonitorTitle: "Moniteur des paires",
    pairMonitorCaption: "Clique sur une paire pour voir l’historique, le raisonnement et l’état de la stratégie.",
    pairDetailTitle: "Détail de la paire",
    pairDetailCaption: "Vue enrichie avec résumé du signal, contexte de tendance et payload brut sur demande.",
    recentRunsTitle: "Dernières exécutions",
    recentRunsCaption: "Journal opérationnel des scans, vues marché et exécutions par paire.",
    pair: "Paire",
    status: "Statut",
    direction: "Direction",
    zScore: "Z-Score",
    conviction: "Conviction",
    divergence: "Divergence",
    correlation: "Corrélation",
    regime: "Régime",
    monitoredPairs: "Paires suivies",
    latestSignals: "Derniers signaux",
    healthySignals: "Signaux valides",
    signalFailures: "Échecs de signal",
    monitoredPairsNote: "Paires incluses dans le scan par défaut.",
    latestSignalsNote: "Paires avec un snapshot de signal enregistré.",
    healthySignalsNote: "Signaux produits sans erreur d’exécution ni de données.",
    signalFailuresNote: "Paires nécessitant une relance, une correction de données ou un meilleur fallback.",
    noDailyOverview: "Aucune vue marché n’a encore été lancée.",
    noPairScan: "Aucun scan de paires n’a encore été lancé.",
    statusLabel: "Statut",
    windowLabel: "Fenêtre",
    messageLabel: "Message",
    signalLabel: "Signal",
    noMessage: "Aucun message",
    noAdditionalSummary: "Aucun résumé supplémentaire disponible.",
    defaultScanSignalSummary: "{ok} ok / {error} erreurs sur {total} paires.",
    runScanToPopulate: "Lance un scan pour remplir le tableau des signaux.",
    dislocation: "Écart",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Aucune exécution enregistrée.",
    unknownPair: "Paire inconnue",
    pairContextLine: "{direction} avec un contexte {divergence}.",
    returnSpread: "Spread de performance",
    baseVsPeer: "Base vs pair",
    operatorNotes: "Notes opérateur",
    summary: "Résumé",
    decision: "Décision",
    riskNotes: "Notes de risque",
    noSummary: "Aucun résumé disponible pour le moment.",
    noDecision: "Aucun texte de décision disponible.",
    noRiskNotes: "Aucune note de risque explicite n’a été renvoyée.",
    zScoreTrend: "Tendance Z-Score",
    savedObservations: "{count} observations enregistrées récentes",
    correlationTrend: "Tendance de corrélation",
    pairStability: "Stabilité de la relation entre les actifs",
    recentHistory: "Historique récent",
    recentSignalSnapshots: "Snapshots de signal les plus récents",
    noHistoryEntries: "Pas encore d’historique.",
    noHistoryYet: "Historique insuffisant pour le moment.",
    needTwoObservations: "Il faut au moins 2 observations enregistrées pour tracer une tendance.",
    rawStrategyPayload: "Payload brut de la stratégie",
    rawPayloadCaption: "Disponible à la demande pour debug, audit ou export.",
    showJson: "Afficher le JSON",
    hideJson: "Masquer le JSON",
    noPairDetailYet: "Lance un scan de paire pour débloquer l’historique, les graphiques et les notes opérateur.",
    actionRunning: "{label} est en cours...",
    actionSuccess: "{label} terminé avec succès.",
    actionFailed: "{label} a échoué : {error}",
    refreshAction: "Rafraîchissement",
    dailyOverviewAction: "Vue marché",
    defaultScanAction: "Scan par défaut",
    pairScanAction: "Scan de la paire {pair}",
    initialLoadFailed: "Échec du chargement initial : {error}",
    ready: "prêt",
    loading: "chargement",
    running: "en cours",
    unknown: "inconnu",
    ok: "ok",
    error: "erreur",
    partial: "partiel",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Vue marché",
    defaultScanRunType: "Scan par défaut",
    pairScanRunType: "Scan de paire",
    baseOutperforming: "La base surperforme",
    baseLagging: "La base sous-performe",
    broadlyTracking: "Évolution globalement conjointe",
    crisis: "Crise",
    riskOn: "Appétit pour le risque",
    riskOff: "Réduction du risque",
    zScoreHelp:
      "Mesure à quel point la paire s’est éloignée de sa relation habituelle. Une valeur élevée signifie une divergence plus forte et un meilleur candidat au retour à la moyenne.",
    convictionHelp:
      "Confiance globale dans le signal. Une valeur élevée signifie plus de confirmations via le régime de marché, la performance relative et le contexte technique.",
    correlationHelp:
      "Mesure à quel point les deux actifs évoluent habituellement ensemble. Une valeur élevée signifie que la paire est mieux adaptée à l’analyse de divergence et au retour à la moyenne.",
  },
  es: {
    pageTitle: "Centro de control CADR",
    heroEyebrow: "Centro de control CADR",
    heroTitle: "Monitorización cross-asset pensada para decidir, no para leer volcados JSON.",
    heroCopy:
      "Observa la presión de divergencia, la calidad de la señal y el régimen de mercado en una sola pantalla. El payload bruto sigue disponible bajo demanda, pero la interfaz destaca primero lo importante.",
    actionsTitle: "Acciones",
    refreshDashboard: "Actualizar panel",
    runDailyOverview: "Ejecutar resumen diario",
    runPairScan: "Ejecutar escaneo de pares",
    baseAsset: "Activo base",
    quoteAsset: "Activo comparado",
    lookbackDays: "Ventana en días",
    runCustomPair: "Ejecutar par personalizado",
    actionLogIdle: "El panel está esperando la siguiente acción.",
    systemSnapshotTitle: "Estado del sistema",
    systemSnapshotCaption: "Salud general, cadencia y últimas salidas del sistema.",
    latestDailyOverviewTitle: "Último resumen diario",
    latestScanTitle: "Último escaneo",
    signalBoardTitle: "Panel de señales",
    signalBoardCaption: "Las mejores oportunidades y mayores desviaciones, ordenadas visualmente.",
    pairMonitorTitle: "Monitor de pares",
    pairMonitorCaption: "Haz clic en un par para ver historial, razonamiento y estado de la estrategia.",
    pairDetailTitle: "Detalle del par",
    pairDetailCaption: "Vista ampliada con resumen de señal, contexto de tendencia y payload bruto opcional.",
    recentRunsTitle: "Ejecuciones recientes",
    recentRunsCaption: "Registro operativo de escaneos, resúmenes y trabajos por par.",
    pair: "Par",
    status: "Estado",
    direction: "Dirección",
    zScore: "Z-Score",
    conviction: "Convicción",
    divergence: "Divergencia",
    correlation: "Correlación",
    regime: "Régimen",
    monitoredPairs: "Pares monitorizados",
    latestSignals: "Señales recientes",
    healthySignals: "Señales sanas",
    signalFailures: "Fallos de señal",
    monitoredPairsNote: "Pares configurados para el escaneo por defecto.",
    latestSignalsNote: "Pares con una instantánea de señal ya guardada.",
    healthySignalsNote: "Señales generadas sin errores de ejecución ni de datos.",
    signalFailuresNote: "Pares que necesitan reintento, corrección de datos o mejor fallback.",
    noDailyOverview: "Todavía no se ha ejecutado el resumen diario.",
    noPairScan: "Todavía no se ha ejecutado un escaneo de pares.",
    statusLabel: "Estado",
    windowLabel: "Ventana",
    messageLabel: "Mensaje",
    signalLabel: "Señal",
    noMessage: "Sin mensaje",
    noAdditionalSummary: "No hay resumen adicional disponible.",
    defaultScanSignalSummary: "{ok} ok / {error} errores en {total} pares.",
    runScanToPopulate: "Ejecuta un escaneo para rellenar el panel de señales.",
    dislocation: "Desviación",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Todavía no hay ejecuciones registradas.",
    unknownPair: "Par desconocido",
    pairContextLine: "{direction} con contexto {divergence}.",
    returnSpread: "Spread de retorno",
    baseVsPeer: "Base vs par",
    operatorNotes: "Notas del operador",
    summary: "Resumen",
    decision: "Decisión",
    riskNotes: "Notas de riesgo",
    noSummary: "Aún no hay resumen disponible.",
    noDecision: "No hay texto de decisión disponible.",
    noRiskNotes: "No se devolvieron notas de riesgo explícitas.",
    zScoreTrend: "Tendencia Z-Score",
    savedObservations: "Últimas observaciones guardadas: {count}",
    correlationTrend: "Tendencia de correlación",
    pairStability: "Estabilidad de la relación entre activos",
    recentHistory: "Historial reciente",
    recentSignalSnapshots: "Instantáneas de señal más recientes",
    noHistoryEntries: "Todavía no hay historial.",
    noHistoryYet: "Aún no hay suficiente historial.",
    needTwoObservations: "Se necesitan al menos 2 observaciones guardadas para dibujar una tendencia.",
    rawStrategyPayload: "Payload bruto de la estrategia",
    rawPayloadCaption: "Disponible bajo demanda para depuración, auditoría o exportación.",
    showJson: "Mostrar JSON",
    hideJson: "Ocultar JSON",
    noPairDetailYet: "Ejecuta un escaneo de par para ver historial, gráficos y notas del operador.",
    actionRunning: "{label} se está ejecutando...",
    actionSuccess: "{label} terminó correctamente.",
    actionFailed: "{label} falló: {error}",
    refreshAction: "Actualización",
    dailyOverviewAction: "Resumen diario",
    defaultScanAction: "Escaneo por defecto",
    pairScanAction: "Escaneo del par {pair}",
    initialLoadFailed: "La carga inicial falló: {error}",
    ready: "listo",
    loading: "cargando",
    running: "en ejecución",
    unknown: "desconocido",
    ok: "ok",
    error: "error",
    partial: "parcial",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Resumen diario",
    defaultScanRunType: "Escaneo por defecto",
    pairScanRunType: "Escaneo de par",
    baseOutperforming: "La base supera al par",
    baseLagging: "La base se queda atrás",
    broadlyTracking: "Seguimiento amplio",
    crisis: "Crisis",
    riskOn: "Apetito por riesgo",
    riskOff: "Evitación del riesgo",
    zScoreHelp:
      "Indica cuánto se ha separado el par de su relación habitual. Cuanto mayor es el valor, mayor es la divergencia y más interesante es la idea de reversión a la media.",
    convictionHelp:
      "Confianza global en la señal. Un valor más alto significa más evidencia de apoyo desde el régimen de mercado, el rendimiento relativo y el contexto técnico.",
    correlationHelp:
      "Indica cuánto suelen moverse juntos los dos activos. Un valor más alto significa que el par encaja mejor en análisis de divergencia y reversión a la media.",
  },
  it: {
    pageTitle: "Centro di controllo CADR",
    heroEyebrow: "Centro di controllo CADR",
    heroTitle: "Monitoraggio cross-asset pensato per decidere, non per leggere dump JSON grezzi.",
    heroCopy:
      "Osserva pressione di divergenza, qualità del segnale e regime di mercato in un solo schermo. Il payload grezzo resta disponibile su richiesta, ma l’interfaccia mette prima in evidenza ciò che conta.",
    actionsTitle: "Azioni",
    refreshDashboard: "Aggiorna dashboard",
    runDailyOverview: "Avvia panoramica giornaliera",
    runPairScan: "Avvia scansione coppie",
    baseAsset: "Asset base",
    quoteAsset: "Asset comparato",
    lookbackDays: "Finestra in giorni",
    runCustomPair: "Avvia coppia personalizzata",
    actionLogIdle: "La dashboard è in attesa della prossima azione.",
    systemSnapshotTitle: "Stato del sistema",
    systemSnapshotCaption: "Salute generale, cadenza e ultime uscite del sistema.",
    latestDailyOverviewTitle: "Ultima panoramica giornaliera",
    latestScanTitle: "Ultima scansione",
    signalBoardTitle: "Bacheca segnali",
    signalBoardCaption: "Le migliori opportunità e le divergenze più forti, ordinate visivamente.",
    pairMonitorTitle: "Monitor coppie",
    pairMonitorCaption: "Clicca su una coppia per vedere storico, ragionamento e stato della strategia.",
    pairDetailTitle: "Dettaglio coppia",
    pairDetailCaption: "Vista estesa con riepilogo del segnale, contesto del trend e payload grezzo opzionale.",
    recentRunsTitle: "Esecuzioni recenti",
    recentRunsCaption: "Registro operativo di scansioni, panoramiche ed esecuzioni per coppia.",
    pair: "Coppia",
    status: "Stato",
    direction: "Direzione",
    zScore: "Z-Score",
    conviction: "Conviction",
    divergence: "Divergenza",
    correlation: "Correlazione",
    regime: "Regime",
    monitoredPairs: "Coppie monitorate",
    latestSignals: "Segnali recenti",
    healthySignals: "Segnali puliti",
    signalFailures: "Errori di segnale",
    monitoredPairsNote: "Coppie configurate per la scansione predefinita.",
    latestSignalsNote: "Coppie con snapshot di segnale già salvato.",
    healthySignalsNote: "Segnali generati senza errori di esecuzione o dati.",
    signalFailuresNote: "Coppie che richiedono retry, fix dei dati o fallback migliore.",
    noDailyOverview: "Nessuna panoramica giornaliera ancora eseguita.",
    noPairScan: "Nessuna scansione coppie ancora eseguita.",
    statusLabel: "Stato",
    windowLabel: "Finestra",
    messageLabel: "Messaggio",
    signalLabel: "Segnale",
    noMessage: "Nessun messaggio",
    noAdditionalSummary: "Nessun riepilogo aggiuntivo disponibile.",
    defaultScanSignalSummary: "{ok} ok / {error} errori su {total} coppie.",
    runScanToPopulate: "Avvia una scansione per riempire la bacheca segnali.",
    dislocation: "Scostamento",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Nessuna esecuzione registrata.",
    unknownPair: "Coppia sconosciuta",
    pairContextLine: "{direction} con contesto {divergence}.",
    returnSpread: "Spread di rendimento",
    baseVsPeer: "Base vs peer",
    operatorNotes: "Note operative",
    summary: "Riepilogo",
    decision: "Decisione",
    riskNotes: "Note di rischio",
    noSummary: "Nessun riepilogo disponibile al momento.",
    noDecision: "Nessun testo decisionale disponibile.",
    noRiskNotes: "Nessuna nota di rischio esplicita restituita.",
    zScoreTrend: "Trend Z-Score",
    savedObservations: "Ultime osservazioni salvate: {count}",
    correlationTrend: "Trend di correlazione",
    pairStability: "Stabilità della relazione della coppia",
    recentHistory: "Storico recente",
    recentSignalSnapshots: "Snapshot di segnale più recenti",
    noHistoryEntries: "Nessuno storico disponibile.",
    noHistoryYet: "Storico ancora insufficiente.",
    needTwoObservations: "Servono almeno 2 osservazioni salvate per disegnare un trend.",
    rawStrategyPayload: "Payload grezzo della strategia",
    rawPayloadCaption: "Disponibile su richiesta per debug, audit o export.",
    showJson: "Mostra JSON",
    hideJson: "Nascondi JSON",
    noPairDetailYet: "Avvia una scansione della coppia per sbloccare storico, grafici e note operative.",
    actionRunning: "{label} è in esecuzione...",
    actionSuccess: "{label} completato con successo.",
    actionFailed: "{label} non riuscito: {error}",
    refreshAction: "Aggiornamento",
    dailyOverviewAction: "Panoramica giornaliera",
    defaultScanAction: "Scansione predefinita",
    pairScanAction: "Scansione coppia {pair}",
    initialLoadFailed: "Caricamento iniziale non riuscito: {error}",
    ready: "pronto",
    loading: "caricamento",
    running: "in esecuzione",
    unknown: "sconosciuto",
    ok: "ok",
    error: "errore",
    partial: "parziale",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Panoramica giornaliera",
    defaultScanRunType: "Scansione predefinita",
    pairScanRunType: "Scansione coppia",
    baseOutperforming: "La base sovraperforma",
    baseLagging: "La base sottoperforma",
    broadlyTracking: "Movimento ampiamente allineato",
    crisis: "Crisi",
    riskOn: "Propensione al rischio",
    riskOff: "Avversione al rischio",
    zScoreHelp:
      "Indica quanto la coppia si è allontanata dalla sua relazione abituale. Valori più alti significano una divergenza più forte e una configurazione più interessante per il ritorno alla media.",
    convictionHelp:
      "Fiducia complessiva nel segnale. Valori più alti significano più conferme da regime di mercato, performance relativa e contesto tecnico.",
    correlationHelp:
      "Indica quanto i due asset si muovono di solito insieme. Valori più alti significano che la coppia è più adatta all’analisi di divergenza e mean reversion.",
  },
  pt: {
    pageTitle: "Sala de controlo CADR",
    heroEyebrow: "Sala de controlo CADR",
    heroTitle: "Monitorização cross-asset feita para decidir, não para ler dumps JSON brutos.",
    heroCopy:
      "Acompanha a pressão de divergência, a qualidade do sinal e o regime de mercado num só ecrã. O payload bruto continua disponível quando necessário, mas a interface mostra primeiro o que importa.",
    actionsTitle: "Ações",
    refreshDashboard: "Atualizar painel",
    runDailyOverview: "Executar visão diária",
    runPairScan: "Executar scan de pares",
    baseAsset: "Ativo base",
    quoteAsset: "Ativo comparado",
    lookbackDays: "Janela em dias",
    runCustomPair: "Executar par personalizado",
    actionLogIdle: "O painel está à espera da próxima ação.",
    systemSnapshotTitle: "Estado do sistema",
    systemSnapshotCaption: "Saúde geral, cadência e últimas saídas do sistema.",
    latestDailyOverviewTitle: "Última visão diária",
    latestScanTitle: "Último scan",
    signalBoardTitle: "Painel de sinais",
    signalBoardCaption: "Melhores oportunidades e maiores desvios, ordenados visualmente.",
    pairMonitorTitle: "Monitor de pares",
    pairMonitorCaption: "Clica num par para ver histórico, raciocínio e estado da estratégia.",
    pairDetailTitle: "Detalhe do par",
    pairDetailCaption: "Vista ampliada com resumo do sinal, contexto de tendência e payload bruto opcional.",
    recentRunsTitle: "Execuções recentes",
    recentRunsCaption: "Registo operacional de scans, visões de mercado e execuções por par.",
    pair: "Par",
    status: "Estado",
    direction: "Direção",
    zScore: "Z-Score",
    conviction: "Convicção",
    divergence: "Divergência",
    correlation: "Correlação",
    regime: "Regime",
    monitoredPairs: "Pares monitorizados",
    latestSignals: "Sinais recentes",
    healthySignals: "Sinais saudáveis",
    signalFailures: "Falhas de sinal",
    monitoredPairsNote: "Pares configurados para o conjunto de scan padrão.",
    latestSignalsNote: "Pares com snapshot de sinal já guardado.",
    healthySignalsNote: "Sinais gerados sem erros de execução ou de dados.",
    signalFailuresNote: "Pares que precisam de nova tentativa, correção de dados ou fallback melhor.",
    noDailyOverview: "Ainda não foi executada nenhuma visão diária.",
    noPairScan: "Ainda não foi executado nenhum scan de pares.",
    statusLabel: "Estado",
    windowLabel: "Janela",
    messageLabel: "Mensagem",
    signalLabel: "Sinal",
    noMessage: "Sem mensagem",
    noAdditionalSummary: "Sem resumo adicional disponível.",
    defaultScanSignalSummary: "{ok} ok / {error} erros em {total} pares.",
    runScanToPopulate: "Executa um scan para preencher o painel de sinais.",
    dislocation: "Deslocamento",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Ainda não há execuções registadas.",
    unknownPair: "Par desconhecido",
    pairContextLine: "{direction} com contexto {divergence}.",
    returnSpread: "Spread de retorno",
    baseVsPeer: "Base vs par",
    operatorNotes: "Notas do operador",
    summary: "Resumo",
    decision: "Decisão",
    riskNotes: "Notas de risco",
    noSummary: "Ainda não há resumo disponível.",
    noDecision: "Sem texto de decisão disponível.",
    noRiskNotes: "Não foram devolvidas notas de risco explícitas.",
    zScoreTrend: "Tendência do Z-Score",
    savedObservations: "Últimas observações guardadas: {count}",
    correlationTrend: "Tendência da correlação",
    pairStability: "Estabilidade da relação entre os ativos",
    recentHistory: "Histórico recente",
    recentSignalSnapshots: "Snapshots de sinal mais recentes",
    noHistoryEntries: "Ainda não há histórico.",
    noHistoryYet: "Ainda não há histórico suficiente.",
    needTwoObservations: "São necessárias pelo menos 2 observações guardadas para desenhar uma tendência.",
    rawStrategyPayload: "Payload bruto da estratégia",
    rawPayloadCaption: "Disponível quando necessário para debug, auditoria ou exportação.",
    showJson: "Mostrar JSON",
    hideJson: "Ocultar JSON",
    noPairDetailYet: "Executa um scan do par para desbloquear histórico, gráficos e notas do operador.",
    actionRunning: "{label} está em execução...",
    actionSuccess: "{label} terminou com sucesso.",
    actionFailed: "{label} falhou: {error}",
    refreshAction: "Atualização",
    dailyOverviewAction: "Visão diária",
    defaultScanAction: "Scan padrão",
    pairScanAction: "Scan do par {pair}",
    initialLoadFailed: "Falha no carregamento inicial: {error}",
    ready: "pronto",
    loading: "a carregar",
    running: "em execução",
    unknown: "desconhecido",
    ok: "ok",
    error: "erro",
    partial: "parcial",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Visão diária",
    defaultScanRunType: "Scan padrão",
    pairScanRunType: "Scan do par",
    baseOutperforming: "A base supera o par",
    baseLagging: "A base fica atrás",
    broadlyTracking: "Movimento amplamente alinhado",
    crisis: "Crise",
    riskOn: "Apetite por risco",
    riskOff: "Aversão ao risco",
    zScoreHelp:
      "Mostra o quanto o par se afastou da sua relação habitual. Valores mais altos significam divergência mais forte e uma ideia mais interessante de reversão à média.",
    convictionHelp:
      "Confiança global no sinal. Valores mais altos significam mais confirmação a partir do regime de mercado, desempenho relativo e contexto técnico.",
    correlationHelp:
      "Mostra o quanto os dois ativos costumam mover-se juntos. Valores mais altos significam que o par é mais adequado para análise de divergência e reversão à média.",
  },
  nl: {
    pageTitle: "CADR Controlekamer",
    heroEyebrow: "CADR Controlekamer",
    heroTitle: "Cross-asset monitoring voor beslissingen, niet voor ruwe JSON-dumps.",
    heroCopy:
      "Volg divergentiedruk, signaalkwaliteit en marktregime op één scherm. De ruwe payload blijft beschikbaar wanneer nodig, maar de interface toont eerst wat echt telt.",
    actionsTitle: "Acties",
    refreshDashboard: "Dashboard vernieuwen",
    runDailyOverview: "Dagoverzicht starten",
    runPairScan: "Pair-scan starten",
    baseAsset: "Basis-asset",
    quoteAsset: "Vergelijkingsasset",
    lookbackDays: "Terugblik in dagen",
    runCustomPair: "Aangepast paar starten",
    actionLogIdle: "Het dashboard wacht op de volgende actie.",
    systemSnapshotTitle: "Systeemoverzicht",
    systemSnapshotCaption: "Algemene gezondheid, cadans en laatste systeemuitvoer.",
    latestDailyOverviewTitle: "Laatste dagoverzicht",
    latestScanTitle: "Laatste scan",
    signalBoardTitle: "Signaalbord",
    signalBoardCaption: "Beste kansen en grootste afwijkingen visueel gerangschikt.",
    pairMonitorTitle: "Paarmonitor",
    pairMonitorCaption: "Klik op een paar om historie, redenering en strategiestatus te bekijken.",
    pairDetailTitle: "Paar-details",
    pairDetailCaption: "Uitgebreide weergave met signaalsamenvatting, trendcontext en optionele ruwe payload.",
    recentRunsTitle: "Recente runs",
    recentRunsCaption: "Operationeel log van scans, overzichten en paarspecifieke runs.",
    pair: "Paar",
    status: "Status",
    direction: "Richting",
    zScore: "Z-Score",
    conviction: "Overtuiging",
    divergence: "Divergentie",
    correlation: "Correlatie",
    regime: "Regime",
    monitoredPairs: "Gevolgde paren",
    latestSignals: "Laatste signalen",
    healthySignals: "Gezonde signalen",
    signalFailures: "Signaalfouten",
    monitoredPairsNote: "Paren in de standaard scan-set.",
    latestSignalsNote: "Paren met een opgeslagen actuele signaalsnapshot.",
    healthySignalsNote: "Signalen zonder uitvoerings- of datafouten.",
    signalFailuresNote: "Paren die een retry, datafix of betere fallback nodig hebben.",
    noDailyOverview: "Er is nog geen dagoverzicht uitgevoerd.",
    noPairScan: "Er is nog geen pair-scan uitgevoerd.",
    statusLabel: "Status",
    windowLabel: "Venster",
    messageLabel: "Bericht",
    signalLabel: "Signaal",
    noMessage: "Geen bericht",
    noAdditionalSummary: "Geen extra samenvatting beschikbaar.",
    defaultScanSignalSummary: "{ok} ok / {error} fouten over {total} paren.",
    runScanToPopulate: "Start een scan om het signaalbord te vullen.",
    dislocation: "Afwijking",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Nog geen runs geregistreerd.",
    unknownPair: "Onbekend paar",
    pairContextLine: "{direction} met context {divergence}.",
    returnSpread: "Rendementsspread",
    baseVsPeer: "Basis vs peer",
    operatorNotes: "Operator-notities",
    summary: "Samenvatting",
    decision: "Beslissing",
    riskNotes: "Risiconotities",
    noSummary: "Nog geen samenvatting beschikbaar.",
    noDecision: "Nog geen beslissingstekst beschikbaar.",
    noRiskNotes: "Geen expliciete risiconotities teruggegeven.",
    zScoreTrend: "Z-Score-trend",
    savedObservations: "Laatste opgeslagen observaties: {count}",
    correlationTrend: "Correlatietrend",
    pairStability: "Stabiliteit van de relatie tussen de assets",
    recentHistory: "Recente historie",
    recentSignalSnapshots: "Meest recente signaalsnapshots",
    noHistoryEntries: "Nog geen historie beschikbaar.",
    noHistoryYet: "Nog niet genoeg historie.",
    needTwoObservations: "Minimaal 2 opgeslagen observaties nodig om een trend te tekenen.",
    rawStrategyPayload: "Ruwe strategie-payload",
    rawPayloadCaption: "Beschikbaar op aanvraag voor debugging, audit of export.",
    showJson: "JSON tonen",
    hideJson: "JSON verbergen",
    noPairDetailYet: "Voer een pair-scan uit om historie, grafieken en operator-notities te ontgrendelen.",
    actionRunning: "{label} wordt uitgevoerd...",
    actionSuccess: "{label} succesvol afgerond.",
    actionFailed: "{label} mislukt: {error}",
    refreshAction: "Vernieuwing",
    dailyOverviewAction: "Dagoverzicht",
    defaultScanAction: "Standaard scan",
    pairScanAction: "Pair-scan {pair}",
    initialLoadFailed: "Eerste laadpoging mislukt: {error}",
    ready: "klaar",
    loading: "laden",
    running: "actief",
    unknown: "onbekend",
    ok: "ok",
    error: "fout",
    partial: "gedeeltelijk",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Dagoverzicht",
    defaultScanRunType: "Standaard scan",
    pairScanRunType: "Pair-scan",
    baseOutperforming: "Basis presteert beter",
    baseLagging: "Basis blijft achter",
    broadlyTracking: "Beweegt grotendeels gelijk",
    crisis: "Crisis",
    riskOn: "Meer risicobereidheid",
    riskOff: "Minder risicobereidheid",
    zScoreHelp:
      "Laat zien hoe ver het paar is afgedreven van zijn normale relatie. Hogere waarden betekenen een sterkere divergentie en een interessantere mean-reversion setup.",
    convictionHelp:
      "Algemene overtuiging in het signaal. Hogere waarden betekenen meer bevestiging vanuit marktregime, relatieve prestatie en technische context.",
    correlationHelp:
      "Laat zien hoe sterk de twee assets normaal samen bewegen. Hogere waarden betekenen dat het paar structureel geschikter is voor divergentie- en mean-reversion-analyse.",
  },
  pl: {
    pageTitle: "Centrum kontroli CADR",
    heroEyebrow: "Centrum kontroli CADR",
    heroTitle: "Monitoring cross-asset do podejmowania decyzji, a nie do oglądania surowych dumpów JSON.",
    heroCopy:
      "Obserwuj siłę dywergencji, jakość sygnału i reżim rynkowy na jednym ekranie. Surowy payload nadal jest dostępny na żądanie, ale interfejs najpierw pokazuje to, co najważniejsze.",
    actionsTitle: "Akcje",
    refreshDashboard: "Odśwież panel",
    runDailyOverview: "Uruchom przegląd dzienny",
    runPairScan: "Uruchom skan par",
    baseAsset: "Aktyw bazowy",
    quoteAsset: "Aktyw porównawczy",
    lookbackDays: "Okno w dniach",
    runCustomPair: "Uruchom własną parę",
    actionLogIdle: "Panel czeka na kolejną akcję.",
    systemSnapshotTitle: "Stan systemu",
    systemSnapshotCaption: "Ogólna kondycja, rytm i ostatnie wyniki systemu.",
    latestDailyOverviewTitle: "Ostatni przegląd dzienny",
    latestScanTitle: "Ostatni skan",
    signalBoardTitle: "Tablica sygnałów",
    signalBoardCaption: "Najlepsze okazje i największe odchylenia posortowane wizualnie.",
    pairMonitorTitle: "Monitor par",
    pairMonitorCaption: "Kliknij parę, aby zobaczyć historię, uzasadnienie i stan strategii.",
    pairDetailTitle: "Szczegóły pary",
    pairDetailCaption: "Rozszerzony widok z podsumowaniem sygnału, kontekstem trendu i opcjonalnym surowym payloadem.",
    recentRunsTitle: "Ostatnie uruchomienia",
    recentRunsCaption: "Dziennik operacyjny skanów, przeglądów i zadań dla konkretnych par.",
    pair: "Para",
    status: "Status",
    direction: "Kierunek",
    zScore: "Z-Score",
    conviction: "Pewność",
    divergence: "Dywergencja",
    correlation: "Korelacja",
    regime: "Reżim",
    monitoredPairs: "Monitorowane pary",
    latestSignals: "Najnowsze sygnały",
    healthySignals: "Poprawne sygnały",
    signalFailures: "Błędy sygnałów",
    monitoredPairsNote: "Pary skonfigurowane w domyślnym zestawie skanowania.",
    latestSignalsNote: "Pary z zapisanym aktualnym snapshotem sygnału.",
    healthySignalsNote: "Sygnały wygenerowane bez błędów wykonania lub danych.",
    signalFailuresNote: "Pary wymagające ponowienia, poprawy danych lub lepszego fallbacku.",
    noDailyOverview: "Przegląd dzienny nie był jeszcze uruchamiany.",
    noPairScan: "Skan par nie był jeszcze uruchamiany.",
    statusLabel: "Status",
    windowLabel: "Okno",
    messageLabel: "Komunikat",
    signalLabel: "Sygnał",
    noMessage: "Brak komunikatu",
    noAdditionalSummary: "Brak dodatkowego podsumowania.",
    defaultScanSignalSummary: "{ok} ok / {error} błędów dla {total} par.",
    runScanToPopulate: "Uruchom skan, aby wypełnić tablicę sygnałów.",
    dislocation: "Odchylenie",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Brak zapisanych uruchomień.",
    unknownPair: "Nieznana para",
    pairContextLine: "{direction} przy kontekście {divergence}.",
    returnSpread: "Spread stopy zwrotu",
    baseVsPeer: "Baza vs para",
    operatorNotes: "Notatki operatora",
    summary: "Podsumowanie",
    decision: "Decyzja",
    riskNotes: "Notatki o ryzyku",
    noSummary: "Brak dostępnego podsumowania.",
    noDecision: "Brak dostępnego tekstu decyzji.",
    noRiskNotes: "Brak jawnych notatek o ryzyku.",
    zScoreTrend: "Trend Z-Score",
    savedObservations: "Ostatnie zapisane obserwacje: {count}",
    correlationTrend: "Trend korelacji",
    pairStability: "Stabilność relacji między aktywami",
    recentHistory: "Najnowsza historia",
    recentSignalSnapshots: "Najświeższe snapshoty sygnałów",
    noHistoryEntries: "Brak historii.",
    noHistoryYet: "Historia jest jeszcze zbyt krótka.",
    needTwoObservations: "Potrzeba co najmniej 2 zapisanych obserwacji, aby narysować trend.",
    rawStrategyPayload: "Surowy payload strategii",
    rawPayloadCaption: "Dostępny na żądanie do debugowania, audytu lub eksportu.",
    showJson: "Pokaż JSON",
    hideJson: "Ukryj JSON",
    noPairDetailYet: "Uruchom skan pary, aby odblokować historię, wykresy i notatki operatora.",
    actionRunning: "{label} trwa...",
    actionSuccess: "{label} zakończono pomyślnie.",
    actionFailed: "{label} zakończono błędem: {error}",
    refreshAction: "Odświeżenie",
    dailyOverviewAction: "Przegląd dzienny",
    defaultScanAction: "Skan domyślny",
    pairScanAction: "Skan pary {pair}",
    initialLoadFailed: "Początkowe ładowanie nie powiodło się: {error}",
    ready: "gotowe",
    loading: "ładowanie",
    running: "w toku",
    unknown: "nieznane",
    ok: "ok",
    error: "błąd",
    partial: "częściowy",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Przegląd dzienny",
    defaultScanRunType: "Skan domyślny",
    pairScanRunType: "Skan pary",
    baseOutperforming: "Baza zachowuje się lepiej",
    baseLagging: "Baza zostaje w tyle",
    broadlyTracking: "Ruch w dużej mierze wspólny",
    crisis: "Kryzys",
    riskOn: "Większa skłonność do ryzyka",
    riskOff: "Mniejsza skłonność do ryzyka",
    zScoreHelp:
      "Pokazuje, jak daleko para odeszła od swojej zwykłej relacji. Wyższe wartości oznaczają silniejszą dywergencję i ciekawszy układ pod mean reversion.",
    convictionHelp:
      "Łączna pewność sygnału. Wyższe wartości oznaczają więcej potwierdzeń ze strony reżimu rynku, relatywnej stopy zwrotu i kontekstu technicznego.",
    correlationHelp:
      "Pokazuje, jak silnie dwa aktywa zwykle poruszają się razem. Wyższe wartości oznaczają, że para lepiej nadaje się do analizy dywergencji i mean reversion.",
  },
  uk: {
    pageTitle: "Пульт CADR",
    heroEyebrow: "Пульт CADR",
    heroTitle: "Cross-asset моніторинг для рішень, а не для перегляду сирих JSON-дампів.",
    heroCopy:
      "Стеж за силою розходження, якістю сигналу та ринковим режимом на одному екрані. Сирий payload залишається доступним на вимогу, але інтерфейс спочатку показує головне.",
    actionsTitle: "Дії",
    refreshDashboard: "Оновити дашборд",
    runDailyOverview: "Запустити денний огляд",
    runPairScan: "Запустити скан пар",
    baseAsset: "Базовий актив",
    quoteAsset: "Порівнюваний актив",
    lookbackDays: "Вікно, днів",
    runCustomPair: "Запустити власну пару",
    actionLogIdle: "Дашборд очікує наступної дії.",
    systemSnapshotTitle: "Стан системи",
    systemSnapshotCaption: "Загальне здоров’я, ритм запусків і останні результати системи.",
    latestDailyOverviewTitle: "Останній денний огляд",
    latestScanTitle: "Останній скан",
    signalBoardTitle: "Дошка сигналів",
    signalBoardCaption: "Найкращі можливості та найбільші відхилення, відсортовані візуально.",
    pairMonitorTitle: "Монітор пар",
    pairMonitorCaption: "Натисни на пару, щоб подивитися історію, аргументацію та стан стратегії.",
    pairDetailTitle: "Деталі пари",
    pairDetailCaption: "Розширений вигляд із підсумком сигналу, контекстом тренду та сирим payload за потреби.",
    recentRunsTitle: "Останні запуски",
    recentRunsCaption: "Операційний журнал сканів, оглядів і точкових запусків по парах.",
    pair: "Пара",
    status: "Статус",
    direction: "Напрям",
    zScore: "Z-Score",
    conviction: "Впевненість",
    divergence: "Розходження",
    correlation: "Кореляція",
    regime: "Режим",
    monitoredPairs: "Пари під наглядом",
    latestSignals: "Останні сигнали",
    healthySignals: "Успішні сигнали",
    signalFailures: "Помилки сигналів",
    monitoredPairsNote: "Пари, налаштовані для стандартного набору сканування.",
    latestSignalsNote: "Пари, для яких вже є актуальний збережений знімок сигналу.",
    healthySignalsNote: "Сигнали, отримані без помилок виконання або даних.",
    signalFailuresNote: "Пари, яким потрібен повторний запуск, виправлення даних або кращий fallback.",
    noDailyOverview: "Денний огляд ще не запускався.",
    noPairScan: "Скан пар ще не запускався.",
    statusLabel: "Статус",
    windowLabel: "Інтервал",
    messageLabel: "Повідомлення",
    signalLabel: "Сигнал",
    noMessage: "Немає повідомлення",
    noAdditionalSummary: "Додаткового підсумку поки немає.",
    defaultScanSignalSummary: "{ok} ok / {error} errors across {total} pairs.",
    runScanToPopulate: "Запусти сканування, щоб заповнити дошку сигналів.",
    dislocation: "Відхилення",
    longLabel: "Лонг {asset}",
    shortLabel: "Шорт {asset}",
    noRuns: "Запусків поки немає.",
    unknownPair: "Невідома пара",
    pairContextLine: "{direction} у контексті {divergence}.",
    returnSpread: "Спред доходності",
    baseVsPeer: "База проти пари",
    operatorNotes: "Нотатки оператора",
    summary: "Підсумок",
    decision: "Рішення",
    riskNotes: "Ризики",
    noSummary: "Підсумок поки недоступний.",
    noDecision: "Текст рішення поки недоступний.",
    noRiskNotes: "Явні нотатки про ризики не повернуто.",
    zScoreTrend: "Тренд Z-Score",
    savedObservations: "Останні збережені спостереження: {count}",
    correlationTrend: "Тренд кореляції",
    pairStability: "Стійкість зв’язку між активами",
    recentHistory: "Остання історія",
    recentSignalSnapshots: "Найсвіжіші знімки сигналу",
    noHistoryEntries: "Історії поки немає.",
    noHistoryYet: "Історії поки недостатньо.",
    needTwoObservations: "Потрібно щонайменше 2 збережені спостереження, щоб побудувати тренд.",
    rawStrategyPayload: "Сирий payload стратегії",
    rawPayloadCaption: "Доступний за потреби для дебагу, аудиту або експорту.",
    showJson: "Показати JSON",
    hideJson: "Сховати JSON",
    noPairDetailYet: "Запусти скан пари, щоб відкрити історію, графіки та нотатки оператора.",
    actionRunning: "{label} виконується...",
    actionSuccess: "{label} успішно завершено.",
    actionFailed: "{label} завершився з помилкою: {error}",
    refreshAction: "Оновлення",
    dailyOverviewAction: "Денний огляд",
    defaultScanAction: "Скан за замовчуванням",
    pairScanAction: "Скан пари {pair}",
    initialLoadFailed: "Початкове завантаження не вдалося: {error}",
    ready: "готово",
    loading: "завантаження",
    running: "виконується",
    unknown: "невідомо",
    ok: "ok",
    error: "помилка",
    partial: "частково",
    longWord: "Лонг",
    shortWord: "Шорт",
    dailyOverviewRunType: "Денний огляд",
    defaultScanRunType: "Скан за замовчуванням",
    pairScanRunType: "Скан пари",
    baseOutperforming: "База сильніша за пару",
    baseLagging: "База відстає",
    broadlyTracking: "Рух загалом синхронний",
    crisis: "Криза",
    riskOn: "Схильність до ризику",
    riskOff: "Уникнення ризику",
    zScoreHelp:
      "Показує, наскільки далеко пара відійшла від своєї звичної залежності. Вищі значення означають сильніше розходження і цікавішу ідею на повернення до середнього.",
    convictionHelp:
      "Загальна впевненість у сигналі. Вищі значення означають більше підтверджень з боку ринкового режиму, відносної динаміки та технічного контексту.",
    correlationHelp:
      "Показує, наскільки сильно два активи зазвичай рухаються разом. Вищі значення означають, що пара краще підходить для аналізу розходжень і mean reversion.",
  },
  ro: {
    pageTitle: "Centrul de control CADR",
    heroEyebrow: "Centrul de control CADR",
    heroTitle: "Monitorizare cross-asset construită pentru decizii, nu pentru dump-uri JSON brute.",
    heroCopy:
      "Urmărește presiunea de divergență, calitatea semnalului și regimul de piață pe un singur ecran. Payload-ul brut rămâne disponibil la cerere, dar interfața scoate în față ce contează mai mult.",
    actionsTitle: "Acțiuni",
    refreshDashboard: "Actualizează panoul",
    runDailyOverview: "Rulează rezumatul zilnic",
    runPairScan: "Rulează scanarea perechilor",
    baseAsset: "Activ de bază",
    quoteAsset: "Activ comparat",
    lookbackDays: "Fereastră în zile",
    runCustomPair: "Rulează pereche personalizată",
    actionLogIdle: "Panoul așteaptă următoarea acțiune.",
    systemSnapshotTitle: "Starea sistemului",
    systemSnapshotCaption: "Sănătate generală, cadență și ultimele ieșiri ale sistemului.",
    latestDailyOverviewTitle: "Ultimul rezumat zilnic",
    latestScanTitle: "Ultima scanare",
    signalBoardTitle: "Panoul semnalelor",
    signalBoardCaption: "Cele mai bune oportunități și cele mai mari deviații, ordonate vizual.",
    pairMonitorTitle: "Monitorul perechilor",
    pairMonitorCaption: "Apasă pe o pereche pentru a vedea istoric, raționament și starea strategiei.",
    pairDetailTitle: "Detaliul perechii",
    pairDetailCaption: "Vedere extinsă cu rezumatul semnalului, contextul trendului și payload brut opțional.",
    recentRunsTitle: "Rulări recente",
    recentRunsCaption: "Jurnal operațional pentru scanări, rezumate și joburi pe perechi.",
    pair: "Pereche",
    status: "Status",
    direction: "Direcție",
    zScore: "Z-Score",
    conviction: "Convingere",
    divergence: "Divergență",
    correlation: "Corelație",
    regime: "Regim",
    monitoredPairs: "Perechi monitorizate",
    latestSignals: "Semnale recente",
    healthySignals: "Semnale curate",
    signalFailures: "Eșecuri de semnal",
    monitoredPairsNote: "Perechi configurate în setul implicit de scanare.",
    latestSignalsNote: "Perechi cu snapshot de semnal salvat.",
    healthySignalsNote: "Semnale generate fără erori de execuție sau de date.",
    signalFailuresNote: "Perechi care au nevoie de rerulare, corecție de date sau fallback mai bun.",
    noDailyOverview: "Rezumatul zilnic nu a fost rulat încă.",
    noPairScan: "Scanarea perechilor nu a fost rulată încă.",
    statusLabel: "Status",
    windowLabel: "Fereastră",
    messageLabel: "Mesaj",
    signalLabel: "Semnal",
    noMessage: "Fără mesaj",
    noAdditionalSummary: "Nu există un rezumat suplimentar disponibil.",
    defaultScanSignalSummary: "{ok} ok / {error} erori pentru {total} perechi.",
    runScanToPopulate: "Rulează o scanare pentru a popula panoul semnalelor.",
    dislocation: "Deviație",
    longLabel: "Long {asset}",
    shortLabel: "Short {asset}",
    noRuns: "Nu există rulări înregistrate încă.",
    unknownPair: "Pereche necunoscută",
    pairContextLine: "{direction} cu context {divergence}.",
    returnSpread: "Spread de randament",
    baseVsPeer: "Bază vs pereche",
    operatorNotes: "Note operator",
    summary: "Rezumat",
    decision: "Decizie",
    riskNotes: "Note de risc",
    noSummary: "Rezumatul nu este disponibil încă.",
    noDecision: "Textul deciziei nu este disponibil.",
    noRiskNotes: "Nu au fost returnate note explicite de risc.",
    zScoreTrend: "Trend Z-Score",
    savedObservations: "Ultimele observații salvate: {count}",
    correlationTrend: "Trendul corelației",
    pairStability: "Stabilitatea relației dintre active",
    recentHistory: "Istoric recent",
    recentSignalSnapshots: "Cele mai recente snapshot-uri de semnal",
    noHistoryEntries: "Nu există istoric încă.",
    noHistoryYet: "Încă nu există suficient istoric.",
    needTwoObservations: "Sunt necesare cel puțin 2 observații salvate pentru a desena un trend.",
    rawStrategyPayload: "Payload brut al strategiei",
    rawPayloadCaption: "Disponibil la cerere pentru debugging, audit sau export.",
    showJson: "Arată JSON",
    hideJson: "Ascunde JSON",
    noPairDetailYet: "Rulează o scanare pe pereche pentru a vedea istoricul, graficele și notele operatorului.",
    actionRunning: "{label} rulează...",
    actionSuccess: "{label} s-a terminat cu succes.",
    actionFailed: "{label} a eșuat: {error}",
    refreshAction: "Actualizare",
    dailyOverviewAction: "Rezumat zilnic",
    defaultScanAction: "Scanare implicită",
    pairScanAction: "Scanare pereche {pair}",
    initialLoadFailed: "Încărcarea inițială a eșuat: {error}",
    ready: "gata",
    loading: "se încarcă",
    running: "în rulare",
    unknown: "necunoscut",
    ok: "ok",
    error: "eroare",
    partial: "parțial",
    longWord: "Long",
    shortWord: "Short",
    dailyOverviewRunType: "Rezumat zilnic",
    defaultScanRunType: "Scanare implicită",
    pairScanRunType: "Scanare pereche",
    baseOutperforming: "Baza depășește perechea",
    baseLagging: "Baza rămâne în urmă",
    broadlyTracking: "Mișcare în linii mari aliniată",
    crisis: "Criză",
    riskOn: "Apetit pentru risc",
    riskOff: "Evitarea riscului",
    zScoreHelp:
      "Arată cât de mult s-a îndepărtat perechea de relația ei obișnuită. Valori mai mari înseamnă divergență mai puternică și o idee mai interesantă de revenire la medie.",
    convictionHelp:
      "Încrederea totală în semnal. Valori mai mari înseamnă mai multe confirmări din regimul de piață, performanța relativă și contextul tehnic.",
    correlationHelp:
      "Arată cât de strâns se mișcă de obicei cele două active împreună. Valori mai mari înseamnă că perechea este mai potrivită pentru analiza divergenței și mean reversion.",
  },
};

const LANGUAGE_FALLBACKS = {
  sv: "en",
  no: "en",
  da: "en",
  fi: "en",
  cs: "en",
  sk: "en",
  hu: "en",
  bg: "en",
  el: "en",
  tr: "en",
};

const LANGUAGE_OPTIONS = [
  { value: "ru", label: "Русский" },
  { value: "en", label: "English" },
  { value: "de", label: "Deutsch" },
  { value: "fr", label: "Français" },
  { value: "es", label: "Español" },
  { value: "it", label: "Italiano" },
  { value: "pt", label: "Português" },
  { value: "nl", label: "Nederlands" },
  { value: "pl", label: "Polski" },
  { value: "uk", label: "Українська" },
  { value: "ro", label: "Română" },
];

const LANGUAGE_STORAGE_KEY = "cadr.dashboard.locale";

const state = {
  dashboard: null,
  selectedPair: null,
  locale: "en",
  localeChoice: "auto",
  busy: {
    active: false,
    label: "",
    startedAt: null,
    timerId: null,
  },
};

function resolveSupportedLocale(candidate) {
  const normalized = String(candidate || "en").toLowerCase();
  const base = normalized.split("-")[0];
  if (TRANSLATIONS[normalized]) {
    return normalized;
  }
  if (TRANSLATIONS[base]) {
    return base;
  }
  if (LANGUAGE_FALLBACKS[base]) {
    return LANGUAGE_FALLBACKS[base];
  }
  return null;
}

function detectLocale() {
  const preferred = [];
  const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
  if (stored && stored !== "auto") {
    preferred.push(stored);
  }
  if (Array.isArray(navigator.languages) && navigator.languages.length > 0) {
    preferred.push(...navigator.languages);
  }
  if (navigator.language) {
    preferred.push(navigator.language);
  }
  const intlLocale = Intl.DateTimeFormat().resolvedOptions().locale;
  if (intlLocale) {
    preferred.push(intlLocale);
  }
  const htmlLocale = document.documentElement.lang;
  if (htmlLocale) {
    preferred.push(htmlLocale);
  }

  for (const candidate of preferred) {
    const resolved = resolveSupportedLocale(candidate);
    if (resolved) {
      return resolved;
    }
  }
  return "en";
}

function t(key, vars = {}) {
  const dictionary = TRANSLATIONS[state.locale] ?? TRANSLATIONS.en;
  const fallback = TRANSLATIONS.en;
  let template = dictionary[key] ?? fallback[key] ?? key;
  for (const [name, value] of Object.entries(vars)) {
    template = template.replaceAll(`{${name}}`, String(value));
  }
  return template;
}

function getResolvedLocaleFromChoice(choice) {
  if (choice && choice !== "auto") {
    return resolveSupportedLocale(choice) ?? "en";
  }
  return detectLocale();
}

function buildLanguageOptions() {
  return [{ value: "auto", label: t("autoLanguage") }, ...LANGUAGE_OPTIONS];
}

function updateLanguageSelector() {
  const select = document.getElementById("language-select");
  if (!select) {
    return;
  }
  select.innerHTML = buildLanguageOptions()
    .map((option) => `<option value="${escapeHtml(option.value)}">${escapeHtml(option.label)}</option>`)
    .join("");
  select.value = state.localeChoice;
}

function setLocaleChoice(choice) {
  state.localeChoice = choice;
  if (choice && choice !== "auto") {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, choice);
  } else {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, "auto");
  }
  state.locale = getResolvedLocaleFromChoice(choice);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function toneClass(status) {
  if (status === "ok") return "tone-ok";
  if (status === "error") return "tone-error";
  return "tone-partial";
}

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return new Intl.NumberFormat(state.locale, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(Number(value));
}

function formatSigned(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return new Intl.NumberFormat(state.locale, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    signDisplay: "exceptZero",
  }).format(Number(value));
}

function formatDateTime(value, fallbackKey = "running") {
  if (!value) {
    return t(fallbackKey);
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  return new Intl.DateTimeFormat(state.locale, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function localizeStatus(status) {
  return t(String(status || "unknown").toLowerCase());
}

function localizeRunType(runType) {
  const mapping = {
    daily_overview: "dailyOverviewRunType",
    default_scan: "defaultScanRunType",
    pair_scan: "pairScanRunType",
    monitor_scan: "runMonitorAction",
  };
  return t(mapping[runType] ?? runType);
}

function localizeOutcome(value) {
  if (!value) {
    return t("pendingOutcome");
  }
  const mapping = {
    pending: "pendingOutcome",
    evaluated: "evaluatedOutcome",
    win: "win",
    loss: "loss",
    flat: "flat",
  };
  return t(mapping[String(value).toLowerCase()] ?? value);
}

function localizeEnum(value) {
  if (!value) {
    return "—";
  }
  const normalized = String(value).toLowerCase();
  const mapping = {
    base_outperforming: "baseOutperforming",
    base_lagging: "baseLagging",
    broadly_tracking: "broadlyTracking",
    crisis: "crisis",
    risk_on: "riskOn",
    risk_off: "riskOff",
  };
  if (mapping[normalized]) {
    return t(mapping[normalized]);
  }
  return String(value)
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function getTradeLegs(signal) {
  const direction = String(signal?.direction ?? "");
  const underscored = direction.match(/long_([a-z0-9]+)_short_([a-z0-9]+)/i);
  if (underscored) {
    return {
      longAsset: underscored[1].toUpperCase(),
      shortAsset: underscored[2].toUpperCase(),
    };
  }

  const spaced = direction.match(/long\s+([a-z0-9]+)\s+short\s+([a-z0-9]+)/i);
  if (spaced) {
    return {
      longAsset: spaced[1].toUpperCase(),
      shortAsset: spaced[2].toUpperCase(),
    };
  }

  return {
    longAsset: signal?.quote_asset ?? "—",
    shortAsset: signal?.base_asset ?? "—",
  };
}

function formatDirection(signal) {
  const legs = getTradeLegs(signal);
  return `${t("longWord")} ${legs.longAsset} / ${t("shortWord")} ${legs.shortAsset}`;
}

function interpolateDirectionText(value) {
  if (!value) {
    return "—";
  }
  const signal = { direction: value };
  return formatDirection(signal);
}

function metricLabel(labelKey, helpKey) {
  return `
    <span class="metric-label">
      ${escapeHtml(t(labelKey))}
      <span class="metric-help" title="${escapeHtml(t(helpKey))}" aria-label="${escapeHtml(t(helpKey))}">?</span>
    </span>
  `;
}

function metricChip(labelKey, value, helpKey = null) {
  const labelContent = helpKey
    ? `${escapeHtml(t(labelKey))} <span class="metric-help" title="${escapeHtml(t(helpKey))}" aria-label="${escapeHtml(t(helpKey))}">?</span>`
    : escapeHtml(t(labelKey));
  return `
    <div class="detail-chip">
      <strong>${labelContent}</strong>
      ${escapeHtml(value)}
    </div>
  `;
}

function setActionLog(message, status = "partial") {
  const el = document.getElementById("action-log");
  el.className = `callout ${toneClass(status)}`;
  el.textContent = message;
}

function setControlsDisabled(disabled) {
  document.querySelectorAll("button, input, textarea, select").forEach((element) => {
    element.disabled = disabled;
  });
}

function refreshBusyTimer() {
  const timer = document.getElementById("busy-timer");
  if (!timer || !state.busy.active || !state.busy.startedAt) {
    return;
  }
  const elapsedSec = Math.max(0, Math.floor((Date.now() - state.busy.startedAt) / 1000));
  timer.textContent = `${elapsedSec}s`;
}

function setBusyState(active, label = "") {
  const indicator = document.getElementById("busy-indicator");
  const title = document.getElementById("busy-title");
  const subtitle = document.getElementById("busy-subtitle");
  const timer = document.getElementById("busy-timer");
  if (!indicator || !title || !subtitle || !timer) {
    return;
  }

  if (state.busy.timerId) {
    clearInterval(state.busy.timerId);
    state.busy.timerId = null;
  }

  state.busy.active = active;
  state.busy.label = label;
  state.busy.startedAt = active ? Date.now() : null;

  if (active) {
    title.textContent = label || t("busyTitle");
    subtitle.textContent = t("busySubtitle");
    timer.textContent = "0s";
    indicator.classList.add("active");
    indicator.setAttribute("aria-hidden", "false");
    state.busy.timerId = setInterval(refreshBusyTimer, 1000);
  } else {
    indicator.classList.remove("active");
    indicator.setAttribute("aria-hidden", "true");
    title.textContent = t("busyTitle");
    subtitle.textContent = t("busySubtitle");
    timer.textContent = "0s";
  }

  setControlsDisabled(active);
}

function applyStaticTranslations() {
  document.documentElement.lang = state.locale;
  document.title = t("pageTitle");
  const mappings = {
    "hero-eyebrow": "heroEyebrow",
    "hero-title": "heroTitle",
    "hero-copy": "heroCopy",
    "actions-title": "actionsTitle",
    "language-label": "languageLabel",
    "refresh-dashboard": "refreshDashboard",
    "run-daily": "runDailyOverview",
    "run-default-scan": "runPairScan",
    "label-base-asset": "baseAsset",
    "label-quote-asset": "quoteAsset",
    "label-lookback-days": "lookbackDays",
    "run-custom-pair": "runCustomPair",
    "system-snapshot-title": "systemSnapshotTitle",
    "system-snapshot-caption": "systemSnapshotCaption",
    "latest-overview-title": "latestDailyOverviewTitle",
    "latest-scan-title": "latestScanTitle",
    "signal-board-title": "signalBoardTitle",
    "signal-board-caption": "signalBoardCaption",
    "pair-monitor-title": "pairMonitorTitle",
    "pair-monitor-caption": "pairMonitorCaption",
    "pair-detail-title": "pairDetailTitle",
    "pair-detail-caption": "pairDetailCaption",
    "recent-runs-title": "recentRunsTitle",
    "recent-runs-caption": "recentRunsCaption",
    "watchlist-title": "watchlistTitle",
    "watchlist-caption": "watchlistCaption",
    "watchlist-enabled-label": "backgroundMonitor",
    "monitor-interval-label": "intervalMinutes",
    "monitor-lookback-label": "monitorLookbackDays",
    "watchlist-editor-label": "watchlistEditorLabel",
    "save-watchlist": "saveWatchlist",
    "run-monitor-now": "runMonitorNow",
    "save-snapshot": "saveSnapshot",
    "evaluate-snapshot": "evaluateSnapshot",
    "evaluate-forecasts": "evaluateForecasts",
    "forecast-summary-title": "forecastSummaryTitle",
    "recent-forecasts-title": "recentForecastsTitle",
    "snapshot-summary-title": "snapshotSummaryTitle",
    "snapshot-evaluation-title": "snapshotEvaluationTitle",
    "th-pair": "pair",
    "th-status": "status",
    "th-direction": "direction",
    "th-zscore": "zScore",
    "th-conviction": "conviction",
    "th-divergence": "divergence",
    "th-correlation": "correlation",
    "th-regime": "regime",
  };

  for (const [id, key] of Object.entries(mappings)) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = t(key);
    }
  }

  updateLanguageSelector();

  const statusEl = document.getElementById("snapshot-status");
  if (statusEl && !state.dashboard) {
    statusEl.textContent = t("loading");
  }

  const busyTitle = document.getElementById("busy-title");
  const busySubtitle = document.getElementById("busy-subtitle");
  if (busyTitle && !state.busy.active) {
    busyTitle.textContent = t("busyTitle");
  }
  if (busySubtitle && !state.busy.active) {
    busySubtitle.textContent = t("busySubtitle");
  }

  if (!state.dashboard && !document.getElementById("action-log").dataset.userSet) {
    setActionLog(t("actionLogIdle"));
  }

  const watchlistStatus = document.getElementById("watchlist-status");
  if (watchlistStatus && !watchlistStatus.dataset.userSet) {
    watchlistStatus.textContent = t("watchlistStatusIdle");
  }
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  return response.json();
}

function buildMetricBar(value, maxValue = 1) {
  const safeValue = value === null || value === undefined ? 0 : Math.abs(Number(value));
  const width = Math.min(100, Math.round((safeValue / maxValue) * 100));
  return `
    <div class="metric-bar">
      <div class="metric-bar-fill" style="width: ${width}%"></div>
    </div>
  `;
}

function buildSparkline(points, color) {
  const values = points.filter((value) => value !== null && value !== undefined && Number.isFinite(Number(value))).map(Number);
  if (values.length === 0) {
    return `<div class="muted">${escapeHtml(t("noHistoryYet"))}</div>`;
  }

  if (values.length === 1) {
    return `<div class="muted">${escapeHtml(t("needTwoObservations"))}</div>`;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stepX = 180 / (values.length - 1);
  const coordinates = values.map((value, index) => {
    const x = index * stepX;
    const y = 74 - ((value - min) / range) * 60;
    return [x, y];
  });
  const polyline = coordinates.map(([x, y]) => `${x},${y}`).join(" ");
  const fillPath = `M0 80 L${polyline} L180 80 Z`;

  return `
    <svg class="sparkline" viewBox="0 0 180 88" preserveAspectRatio="none" aria-hidden="true">
      <path class="sparkline-grid" d="M0 22 H180 M0 44 H180 M0 66 H180"></path>
      <path class="sparkline-fill" d="${fillPath}" fill="${color}"></path>
      <polyline class="sparkline-line" points="${polyline}" stroke="${color}"></polyline>
    </svg>
  `;
}

function renderStats(stats) {
  const grid = document.getElementById("stats-grid");
  const cards = [
    ["monitoredPairs", stats.monitored_pairs ?? 0, "monitoredPairsNote"],
    ["latestSignals", stats.latest_pairs_available ?? 0, "latestSignalsNote"],
    ["healthySignals", stats.ok_pairs ?? 0, "healthySignalsNote"],
    ["signalFailures", stats.error_pairs ?? 0, "signalFailuresNote"],
    ["forecastPending", stats.pending_forecasts ?? 0, "forecastSummaryTitle"],
    ["forecastEvaluated", stats.evaluated_forecasts ?? 0, "recentForecastsTitle"],
  ];

  grid.innerHTML = cards
    .map(
      ([labelKey, value, noteKey]) => `
        <article class="stat-card">
          <p class="stat-label">${escapeHtml(t(labelKey))}</p>
          <div class="stat-value">${escapeHtml(value)}</div>
          <div class="stat-note">${escapeHtml(t(noteKey))}</div>
        </article>
      `
    )
    .join("");
}

function renderWatchlistPanel(watchlist, monitor, forecasts) {
  const editor = document.getElementById("watchlist-editor");
  const enabled = document.getElementById("watchlist-enabled");
  const interval = document.getElementById("monitor-interval");
  const lookback = document.getElementById("monitor-lookback");
  const status = document.getElementById("watchlist-status");
  const summary = document.getElementById("forecast-summary");

  editor.value = (watchlist ?? []).map((entry) => entry.pair).join("\n");
  enabled.checked = Boolean(monitor?.enabled);
  interval.value = Math.max(3, Math.round((monitor?.interval_sec ?? 300) / 60));
  lookback.value = monitor?.lookback_days ?? 90;

  status.textContent =
    `${t("backgroundMonitor")}: ${monitor?.enabled ? t("monitorEnabledYes") : t("monitorEnabledNo")} · ` +
    `${t("monitorNextRun")}: ${formatDateTime(monitor?.next_run_at, "unknown")} · ` +
    `${t("monitorLastRun")}: ${formatDateTime(monitor?.last_finished_at, "unknown")}`;
  status.dataset.userSet = "true";

  const forecastSummary = forecasts?.summary ?? {};
  summary.innerHTML = `
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastPending"))}</span><strong>${escapeHtml(forecastSummary.pending ?? 0)}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastEvaluated"))}</span><strong>${escapeHtml(forecastSummary.evaluated ?? 0)}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastWins"))}</span><strong class="tone-ok">${escapeHtml(forecastSummary.wins ?? 0)}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastLosses"))}</span><strong class="tone-error">${escapeHtml(forecastSummary.losses ?? 0)}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastFlat"))}</span><strong>${escapeHtml(forecastSummary.flat ?? 0)}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("exportPath"))}</span><span>${escapeHtml(forecasts?.export_path ?? "—")}</span></div>
  `;
}

function renderForecasts(forecasts) {
  const container = document.getElementById("recent-forecasts");
  const items = forecasts?.recent ?? [];
  if (items.length === 0) {
    container.innerHTML = `<div class="muted">${escapeHtml(t("noForecasts"))}</div>`;
    return;
  }

  container.innerHTML = items
    .map((item) => `
      <article class="forecast-card">
        <div class="forecast-card-head">
          <strong>${escapeHtml(item.pair)}</strong>
          <span class="status-pill ${item.status === "evaluated" && item.outcome === "win" ? "tone-ok" : item.status === "evaluated" && item.outcome === "loss" ? "tone-error" : "tone-partial"}">
            ${escapeHtml(localizeOutcome(item.outcome ?? item.status))}
          </span>
        </div>
        <div class="forecast-card-meta">
          <span>${escapeHtml(interpolateDirectionText(item.direction))}</span>
          <span>${escapeHtml(t("entryCheckpoint"))}: ${escapeHtml(formatDateTime(item.created_at, "unknown"))}</span>
          <span>${escapeHtml(t("dueAt"))}: ${escapeHtml(formatDateTime(item.due_at, "unknown"))}</span>
        </div>
        <div class="forecast-card-meta">
          <span>${escapeHtml(t("zScore"))}: ${escapeHtml(formatSigned(item.spread_zscore))}</span>
          <span>${escapeHtml(t("conviction"))}: ${escapeHtml(item.conviction_score ?? "—")}</span>
          <span>${escapeHtml(t("correlation"))}: ${escapeHtml(formatNumber(item.correlation, 3))}</span>
          <span>${escapeHtml(t("outcome"))}: ${escapeHtml(item.pnl_pct === null || item.pnl_pct === undefined ? "—" : `${formatSigned(item.pnl_pct)}%`)}</span>
        </div>
      </article>
    `)
    .join("");
}

function renderSnapshotTools(snapshotState) {
  const summary = document.getElementById("snapshot-summary");
  const evaluation = document.getElementById("snapshot-evaluation");
  const latestSnapshot = snapshotState?.latest_snapshot;
  const latestEvaluation = snapshotState?.latest_evaluation;

  if (!latestSnapshot) {
    summary.innerHTML = `<div class="muted">${escapeHtml(t("noSnapshotYet"))}</div>`;
  } else {
    summary.innerHTML = `
      <div class="summary-line"><span class="summary-label">${escapeHtml(t("snapshotGeneratedAt"))}</span><strong>${escapeHtml(formatDateTime(latestSnapshot.generated_at, "unknown"))}</strong></div>
      <div class="summary-line"><span class="summary-label">${escapeHtml(t("snapshotPairs"))}</span><span>${escapeHtml(latestSnapshot.latest_pair_count ?? 0)}</span></div>
      <div class="summary-line"><span class="summary-label">${escapeHtml(t("snapshotPath"))}</span><span>${escapeHtml(snapshotState?.latest_snapshot_path ?? "—")}</span></div>
    `;
  }

  if (!latestEvaluation) {
    evaluation.innerHTML = `<div class="muted">${escapeHtml(t("noSnapshotEvaluationYet"))}</div>`;
    return;
  }

  const stats = latestEvaluation.summary ?? {};
  evaluation.innerHTML = `
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("evaluationAt"))}</span><strong>${escapeHtml(formatDateTime(latestEvaluation.evaluated_at, "unknown"))}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastWins"))}</span><strong class="tone-ok">${escapeHtml(stats.wins ?? 0)}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastLosses"))}</span><strong class="tone-error">${escapeHtml(stats.losses ?? 0)}</strong></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("forecastFlat"))}</span><span>${escapeHtml(stats.flat ?? 0)}</span></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("skipped"))}</span><span>${escapeHtml(stats.skipped ?? 0)}</span></div>
    <div class="summary-line"><span class="summary-label">${escapeHtml(t("evaluationFile"))}</span><span>${escapeHtml(latestEvaluation.output_path ?? "—")}</span></div>
  `;
}

function renderRunSummary(containerId, run, emptyTextKey) {
  const container = document.getElementById(containerId);
  if (!run) {
    container.innerHTML = `<div class="muted">${escapeHtml(t(emptyTextKey))}</div>`;
    return;
  }

  const payload = run.payload ?? {};
  const extraLine =
    run.run_type === "default_scan"
      ? t("defaultScanSignalSummary", {
          ok: payload.ok_count ?? 0,
          error: payload.error_count ?? 0,
          total: payload.total_pairs ?? 0,
        })
      : payload.summary || payload.market_view || payload.pair || null;

  container.innerHTML = `
    <div class="summary-line">
      <span class="summary-label">${escapeHtml(t("statusLabel"))}</span>
      <strong class="${toneClass(run.status)}">${escapeHtml(localizeStatus(run.status))}</strong>
    </div>
    <div class="summary-line">
      <span class="summary-label">${escapeHtml(t("windowLabel"))}</span>
      <span>${escapeHtml(formatDateTime(run.started_at, "unknown"))} → ${escapeHtml(formatDateTime(run.finished_at, "running"))}</span>
    </div>
    <div class="summary-line">
      <span class="summary-label">${escapeHtml(t("messageLabel"))}</span>
      <span>${escapeHtml(run.message ?? run.error ?? t("noMessage"))}</span>
    </div>
    <div class="summary-line">
      <span class="summary-label">${escapeHtml(t("signalLabel"))}</span>
      <span>${escapeHtml(extraLine ?? t("noAdditionalSummary"))}</span>
    </div>
  `;
}

function renderSignalBoard(pairs) {
  const board = document.getElementById("signal-board");
  const rankedPairs = [...pairs].sort((left, right) => Math.abs(right.spread_zscore ?? 0) - Math.abs(left.spread_zscore ?? 0));

  if (rankedPairs.length === 0) {
    board.innerHTML = `<div class="muted">${escapeHtml(t("runScanToPopulate"))}</div>`;
    return;
  }

  board.innerHTML = rankedPairs
    .map((pair) => {
      const isActive = state.selectedPair === pair.pair ? "active" : "";
      const legs = getTradeLegs(pair);
      return `
        <article class="signal-card ${isActive}" data-pair="${escapeHtml(pair.pair)}">
          <div class="signal-card-top">
            <div>
              <strong>${escapeHtml(pair.pair)}</strong>
              <div class="signal-card-meta">${escapeHtml(formatDirection(pair))}</div>
            </div>
            <span class="status-pill ${toneClass(pair.status)}">${escapeHtml(localizeStatus(pair.status))}</span>
          </div>

          <div class="signal-card-meta">
            ${escapeHtml(localizeEnum(pair.divergence_state))} · ${escapeHtml(localizeEnum(pair.market_regime))}
          </div>

          <div class="signal-tags">
            <span class="signal-tag signal-tag-long">${escapeHtml(t("longLabel", { asset: legs.longAsset }))}</span>
            <span class="signal-tag signal-tag-short">${escapeHtml(t("shortLabel", { asset: legs.shortAsset }))}</span>
          </div>

          <div class="metric-rail">
            <div class="metric-row">
              <div class="metric-row-head">
                ${metricLabel("dislocation", "zScoreHelp")}
                <strong>${escapeHtml(formatSigned(pair.spread_zscore))}</strong>
              </div>
              ${buildMetricBar(pair.spread_zscore, 5)}
            </div>
            <div class="metric-row">
              <div class="metric-row-head">
                ${metricLabel("conviction", "convictionHelp")}
                <strong>${escapeHtml(pair.conviction_score ?? "—")}</strong>
              </div>
              ${buildMetricBar(pair.conviction_score, 5)}
            </div>
            <div class="metric-row">
              <div class="metric-row-head">
                ${metricLabel("correlation", "correlationHelp")}
                <strong>${escapeHtml(formatNumber(pair.correlation, 3))}</strong>
              </div>
              ${buildMetricBar(pair.correlation, 1)}
            </div>
          </div>
        </article>
      `;
    })
    .join("");

  board.querySelectorAll(".signal-card").forEach((card) => {
    card.addEventListener("click", () => selectPair(card.dataset.pair));
  });
}

function renderPairTable(pairs) {
  const tbody = document.getElementById("pair-table-body");
  tbody.innerHTML = pairs
    .map((pair) => {
      const active = state.selectedPair === pair.pair ? "active" : "";
      return `
        <tr class="clickable ${active}" data-pair="${escapeHtml(pair.pair)}">
          <td>${escapeHtml(pair.pair)}</td>
          <td class="${toneClass(pair.status)}">${escapeHtml(localizeStatus(pair.status))}</td>
          <td>${escapeHtml(formatDirection(pair))}</td>
          <td>${escapeHtml(formatSigned(pair.spread_zscore))}</td>
          <td>${escapeHtml(pair.conviction_score ?? "—")}</td>
          <td>${escapeHtml(localizeEnum(pair.divergence_state))}</td>
          <td>${escapeHtml(formatNumber(pair.correlation, 3))}</td>
          <td>${escapeHtml(localizeEnum(pair.market_regime))}</td>
        </tr>
      `;
    })
    .join("");

  tbody.querySelectorAll("tr").forEach((row) => {
    row.addEventListener("click", () => {
      selectPair(row.dataset.pair);
    });
  });

  const zHeader = document.getElementById("th-zscore");
  const convictionHeader = document.getElementById("th-conviction");
  const correlationHeader = document.getElementById("th-correlation");
  if (zHeader) zHeader.title = t("zScoreHelp");
  if (convictionHeader) convictionHeader.title = t("convictionHelp");
  if (correlationHeader) correlationHeader.title = t("correlationHelp");
}

function renderRuns(runs) {
  const list = document.getElementById("runs-list");
  if (runs.length === 0) {
    list.innerHTML = `<div class="muted">${escapeHtml(t("noRuns"))}</div>`;
    return;
  }

  list.innerHTML = runs
    .map(
      (run) => `
        <article class="run-card">
          <strong>${escapeHtml(localizeRunType(run.run_type))}${run.pair ? ` · ${escapeHtml(run.pair)}` : ""}</strong>
          <div class="run-meta ${toneClass(run.status)}">${escapeHtml(localizeStatus(run.status))}</div>
          <div class="run-meta">${escapeHtml(formatDateTime(run.started_at, "unknown"))} → ${escapeHtml(formatDateTime(run.finished_at, "running"))}</div>
          <div>${escapeHtml(run.message ?? run.error ?? t("noMessage"))}</div>
        </article>
      `
    )
    .join("");
}

function renderPairDetail(detail) {
  const container = document.getElementById("pair-detail");
  const latest = detail.latest ?? {};
  const history = [...(detail.history ?? [])].reverse();
  const spec = latest.spec ?? {};
  const evidence = spec.analysis?.skill_hub_pair_context ?? {};
  const riskNotes = evidence.risk_notes ?? [];
  const legs = getTradeLegs(latest);

  const zscoreSeries = history.map((entry) => entry.spread_zscore);
  const correlationSeries = history.map((entry) => entry.correlation);
  const historyRows = history
    .slice(-6)
    .reverse()
    .map(
      (entry) => `
        <div class="history-row">
          <div>
            <strong>${escapeHtml(formatSigned(entry.spread_zscore))}</strong>
            <div class="muted">${escapeHtml(formatDirection(entry))}</div>
          </div>
          <time>${escapeHtml(formatDateTime(entry.created_at, "unknown"))}</time>
        </div>
      `
    )
    .join("");

  container.innerHTML = `
    <div class="detail-layout">
      <section class="detail-section">
        <div class="detail-summary">
          <div>
            <h3>${escapeHtml(latest.pair ?? t("unknownPair"))}</h3>
            <p>${escapeHtml(t("pairContextLine", { direction: formatDirection(latest), divergence: localizeEnum(latest.divergence_state) }))}</p>
            <div class="signal-tags">
              <span class="signal-tag signal-tag-long">${escapeHtml(t("longLabel", { asset: legs.longAsset }))}</span>
              <span class="signal-tag signal-tag-short">${escapeHtml(t("shortLabel", { asset: legs.shortAsset }))}</span>
            </div>
          </div>
          <span class="status-pill ${toneClass(latest.status)}">${escapeHtml(localizeStatus(latest.status))}</span>
        </div>

        <div class="detail-grid">
          ${metricChip("zScore", formatSigned(latest.spread_zscore), "zScoreHelp")}
          ${metricChip("conviction", latest.conviction_score ?? "—", "convictionHelp")}
          ${metricChip("correlation", formatNumber(latest.correlation, 3), "correlationHelp")}
          ${metricChip("regime", localizeEnum(latest.market_regime))}
          ${metricChip("returnSpread", `${formatSigned(latest.base_vs_peer_average_return_pct)}%`)}
          ${metricChip("baseVsPeer", `${latest.base_asset ?? "—"} vs ${latest.quote_asset ?? "—"}`)}
        </div>

        <div class="detail-section" style="margin-top: 16px;">
          <h3>${escapeHtml(t("operatorNotes"))}</h3>
          <div class="insight-list">
            <div class="insight-item"><strong>${escapeHtml(t("summary"))}:</strong> ${escapeHtml(evidence.summary ?? t("noSummary"))}</div>
            <div class="insight-item"><strong>${escapeHtml(t("decision"))}:</strong> ${escapeHtml(evidence.business_decision ?? t("noDecision"))}</div>
            <div class="insight-item"><strong>${escapeHtml(t("riskNotes"))}:</strong> ${escapeHtml(riskNotes.join(" | ") || t("noRiskNotes"))}</div>
          </div>
        </div>
      </section>

      <section class="detail-section chart-panel">
        <div class="chart-card">
          <div class="chart-head">
            <strong>${escapeHtml(t("zScoreTrend"))}</strong>
            <span>${escapeHtml(t("savedObservations", { count: history.length }))}</span>
          </div>
          ${buildSparkline(zscoreSeries, "#cb6e36")}
        </div>

        <div class="chart-card">
          <div class="chart-head">
            <strong>${escapeHtml(t("correlationTrend"))}</strong>
            <span>${escapeHtml(t("pairStability"))}</span>
          </div>
          ${buildSparkline(correlationSeries, "#125e50")}
        </div>

        <div class="chart-card">
          <div class="chart-head">
            <strong>${escapeHtml(t("recentHistory"))}</strong>
            <span>${escapeHtml(t("recentSignalSnapshots"))}</span>
          </div>
          <div class="history-grid">
            ${historyRows || `<div class="muted">${escapeHtml(t("noHistoryEntries"))}</div>`}
          </div>
        </div>
      </section>
    </div>

    <section class="detail-section" style="margin-top: 18px;">
      <div class="panel-header compact">
        <div>
          <h3>${escapeHtml(t("rawStrategyPayload"))}</h3>
          <p class="panel-caption">${escapeHtml(t("rawPayloadCaption"))}</p>
        </div>
        <button type="button" class="ghost-btn" id="toggle-raw-json">${escapeHtml(t("showJson"))}</button>
      </div>
      <div class="json-shell">
        <pre id="raw-json" class="code-box" hidden>${escapeHtml(JSON.stringify(spec && Object.keys(spec).length > 0 ? spec : latest, null, 2))}</pre>
      </div>
    </section>
  `;

  const toggleButton = document.getElementById("toggle-raw-json");
  const rawJson = document.getElementById("raw-json");
  toggleButton.addEventListener("click", () => {
    const isHidden = rawJson.hasAttribute("hidden");
    if (isHidden) {
      rawJson.removeAttribute("hidden");
      toggleButton.textContent = t("hideJson");
    } else {
      rawJson.setAttribute("hidden", "");
      toggleButton.textContent = t("showJson");
    }
  });
}

async function selectPair(pair) {
  const detail = await api(`/api/pairs/${encodeURIComponent(pair)}`);
  state.selectedPair = pair;
  renderPairDetail(detail);
  renderSignalBoard(state.dashboard?.pair_signals ?? []);
  renderPairTable(state.dashboard?.pair_signals ?? []);
}

async function loadDashboard() {
  const data = await api("/api/dashboard");
  state.dashboard = data;
  document.getElementById("snapshot-status").textContent = localizeStatus(data.latest_overview?.status ?? "ready");
  renderStats(data.stats);
  renderRunSummary("latest-overview", data.latest_overview, "noDailyOverview");
  renderRunSummary("latest-scan", data.latest_scan, "noPairScan");
  renderWatchlistPanel(data.watchlist, data.monitor, data.forecasts);
  renderForecasts(data.forecasts);
  renderSnapshotTools(data.snapshots);
  renderSignalBoard(data.pair_signals);
  renderPairTable(data.pair_signals);
  renderRuns(data.recent_runs);

  const availablePairs = data.pair_signals.map((entry) => entry.pair);
  if (state.selectedPair && availablePairs.includes(state.selectedPair)) {
    await selectPair(state.selectedPair);
    return;
  }

  if (availablePairs.length > 0) {
    await selectPair(availablePairs[0]);
    return;
  }

  state.selectedPair = null;
  document.getElementById("pair-detail").innerHTML = `<div class="muted">${escapeHtml(t("noPairDetailYet"))}</div>`;
}

async function runAction(label, fn) {
  try {
    setBusyState(true, label);
    setActionLog(t("actionRunning", { label }));
    document.getElementById("action-log").dataset.userSet = "true";
    const result = await fn();
    setBusyState(false);
    setActionLog(t("actionSuccess", { label }), "ok");
    await loadDashboard();
    return result;
  } catch (error) {
    setBusyState(false);
    setActionLog(t("actionFailed", { label, error: error.message }), "error");
  }
}

state.localeChoice = localStorage.getItem(LANGUAGE_STORAGE_KEY) || "auto";
state.locale = getResolvedLocaleFromChoice(state.localeChoice);
applyStaticTranslations();

document.getElementById("language-select").addEventListener("change", async (event) => {
  setLocaleChoice(event.target.value);
  applyStaticTranslations();
  if (state.dashboard) {
    renderStats(state.dashboard.stats);
    renderRunSummary("latest-overview", state.dashboard.latest_overview, "noDailyOverview");
    renderRunSummary("latest-scan", state.dashboard.latest_scan, "noPairScan");
    renderWatchlistPanel(state.dashboard.watchlist, state.dashboard.monitor, state.dashboard.forecasts);
    renderForecasts(state.dashboard.forecasts);
    renderSnapshotTools(state.dashboard.snapshots);
    renderSignalBoard(state.dashboard.pair_signals);
    renderPairTable(state.dashboard.pair_signals);
    renderRuns(state.dashboard.recent_runs);
    if (state.selectedPair) {
      await selectPair(state.selectedPair);
    } else {
      document.getElementById("pair-detail").innerHTML = `<div class="muted">${escapeHtml(t("noPairDetailYet"))}</div>`;
    }
  }
});

document.getElementById("refresh-dashboard").addEventListener("click", () => runAction(t("refreshAction"), loadDashboard));
document.getElementById("run-daily").addEventListener("click", () =>
  runAction(t("dailyOverviewAction"), () => api("/api/runs/daily-overview", { method: "POST" }))
);
document.getElementById("run-default-scan").addEventListener("click", () =>
  runAction(t("defaultScanAction"), () =>
    api("/api/runs/default-scan", {
      method: "POST",
      body: JSON.stringify({ lookback_days: 90 }),
    })
  )
);

document.getElementById("pair-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    base_asset: document.getElementById("base-asset").value.trim().toUpperCase(),
    quote_asset: document.getElementById("quote-asset").value.trim().toUpperCase(),
    lookback_days: Number(document.getElementById("lookback-days").value),
  };
  const result = await runAction(
    t("pairScanAction", { pair: `${payload.base_asset}/${payload.quote_asset}` }),
    () =>
      api("/api/runs/pair", {
        method: "POST",
        body: JSON.stringify(payload),
      })
  );
  if (result?.pair) {
    await selectPair(result.pair);
  }
});

document.getElementById("save-watchlist").addEventListener("click", async () => {
  const pairs = document
    .getElementById("watchlist-editor")
    .value.split(/\r?\n/)
    .map((value) => value.trim())
    .filter(Boolean);

  const result = await runAction(t("saveWatchlistAction"), () =>
    api("/api/watchlist", {
      method: "PUT",
      body: JSON.stringify({
        pairs,
        enabled: document.getElementById("watchlist-enabled").checked,
        interval_minutes: Number(document.getElementById("monitor-interval").value),
        lookback_days: Number(document.getElementById("monitor-lookback").value),
      }),
    })
  );

  if (result) {
    const status = document.getElementById("watchlist-status");
    status.dataset.userSet = "true";
    status.textContent = t("watchlistSaved");
  }
});

document.getElementById("run-monitor-now").addEventListener("click", () =>
  runAction(t("runMonitorAction"), () => api("/api/monitor/run", { method: "POST" }))
);

document.getElementById("evaluate-forecasts").addEventListener("click", async () => {
  const result = await runAction(t("evaluateForecastsAction"), () =>
    api("/api/forecasts/evaluate", {
      method: "POST",
      body: JSON.stringify({ force: false }),
    })
  );
  if (result) {
    const status = document.getElementById("watchlist-status");
    status.dataset.userSet = "true";
    status.textContent = t("forecastsEvaluated", { count: result.evaluated ?? 0 });
  }
});

document.getElementById("save-snapshot").addEventListener("click", async () => {
  const result = await runAction(t("saveSnapshotAction"), () =>
    api("/api/snapshots/export", {
      method: "POST",
    })
  );
  if (result) {
    const status = document.getElementById("watchlist-status");
    status.dataset.userSet = "true";
    status.textContent = t("snapshotSaved");
  }
});

document.getElementById("evaluate-snapshot").addEventListener("click", async () => {
  const result = await runAction(t("evaluateSnapshotAction"), () =>
    api("/api/snapshots/evaluate", {
      method: "POST",
      body: JSON.stringify({ snapshot_path: null }),
    })
  );
  if (result) {
    const status = document.getElementById("watchlist-status");
    status.dataset.userSet = "true";
    status.textContent = t("snapshotEvaluatedMessage", { count: result.summary?.evaluated ?? 0 });
  }
});

loadDashboard().catch((error) => {
  document.getElementById("action-log").dataset.userSet = "true";
  setActionLog(t("initialLoadFailed", { error: error.message }), "error");
});
