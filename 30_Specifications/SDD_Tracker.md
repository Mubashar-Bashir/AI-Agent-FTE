# SDD Tracker

## Active Feature Tracking

```dataview
TABLE status, current_step, percent, next_step
FROM #FTE-Feature
SORT file.name ASC
```

## All FTE Features

```dataview
TABLE status, current_step, percent, next_step, last_cmd
FROM #FTE-Feature
SORT file.name ASC
```

## Feature: 001-workspace-observer

| Spec Name | Status | Current Step | % | Next Step | Last Command |
|-----------|--------|--------------|---|-----------|--------------|
| 001-workspace-observer | Complete | All Phases Complete | 100 | Ready for Production | /sp.tasks |

## Feature: test_spec

| Spec Name | Status | Current Step | % | Next Step | Last Command |
|-----------|--------|--------------|---|-----------|--------------|
| test_spec | Implementation | Requirements Defined | 0 | Review spec | /sp.tasks |
| test_spec | Implementation | Requirements Defined | 0 | Review spec | /sp.tasks |
| test_spec | Implementation | Requirements Defined | 0 | Review spec | /sp.tasks |
| test_spec | Implementation | Requirements Defined | 0 | Review spec | /sp.tasks |
