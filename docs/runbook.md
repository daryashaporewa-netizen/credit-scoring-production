# Runbook мониторинга Credit Scoring

## Общий порядок реагирования

1. Открыть Alertmanager и определить активный alert, время начала и severity.
2. Проверить соответствующие панели Grafana и логи Loki.
3. Проверить Pod приложения и monitoring stack.
4. Сохранить время инцидента, причину и выполненные действия.
5. После восстановления убедиться, что alert перешёл в состояние resolved.

## CreditScoringApiDown

1. Проверить Deployment и Service командой `kubectl get deployment,service`.
2. Проверить probes и события Deployment.
3. Изучить последние логи backend.
4. Если новая версия не запускается, вернуть предыдущий рабочий image tag.

## CreditScoringHighErrorRate

1. В Grafana определить endpoint и HTTP-статусы с ошибками.
2. Найти соответствующие traceback и exception в Loki.
3. Проверить доступность ONNX-модели и preprocessing artifact.
4. При ошибках новой версии остановить production-развёртывание.

## CreditScoringHighLatency

1. Сравнить p95 latency с request rate и загрузкой узлов.
2. Проверить CPU/memory limits и throttling Pod.
3. Проверить количество реплик и события Kubernetes.
4. При сохранении задержки увеличить ресурсы или число реплик.

## CreditScoringContainerRestarts

1. Выполнить `kubectl describe pod` для перезапускающегося Pod.
2. Проверить причину завершения, probes, OOMKilled и последние логи.
3. Исправить конфигурацию или вернуть предыдущий image tag.

## NodeExporterDown

1. Проверить DaemonSet node-exporter в namespace monitoring.
2. Сопоставить отсутствующий Pod с Kubernetes node.
3. Проверить состояние node и доступность порта 9100.

## CreditScoringErrorsInLogs

1. Открыть Loki-панель за последние 10 минут.
2. Найти повторяющееся сообщение error, exception или traceback.
3. Определить Pod и image tag, с которых начались ошибки.
4. Проверить связанные metric alerts и при необходимости откатить image tag.

## Ограничения учебного окружения

- Prometheus, Loki и Grafana используют emptyDir и теряют данные при
  пересоздании Pod.
- Alertmanager хранит и группирует alerts. Внешний канал уведомлений
  подключается только при наличии адреса Slack, email или webhook.
- Для production необходимо ограничить доступ к Grafana и использовать
  постоянные volumes.
