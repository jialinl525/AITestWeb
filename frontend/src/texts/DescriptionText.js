export const DescriptionText = {
  app: {
    miniCard: 'Unified business view for test management, issue tracking, and model evaluation.',
    login: {
      usernamePlaceholder: 'manager (Admin)',
      passwordPlaceholder: 'Default 123456'
    },
    password: {
      currentPlaceholder: 'Please enter current password',
      newPlaceholder: 'Please enter a new password',
      confirmPlaceholder: 'Please re-enter the new password'
    },
    toast: {
      loginSuccess: 'Login successful',
      loginFailed: 'Invalid username or password',
      newPasswordTooShort: 'New password must be at least 6 characters',
      newPasswordMismatch: 'The two new passwords do not match',
      passwordChangedSuccess: 'Password changed successfully',
      passwordChangedFailed: 'Failed to change password'
    }
  },
  bugs: {
    hero: 'Manage issue lifecycle by severity, status, and assignee to quickly identify high-risk defects and pending actions.',
    sectionMeta: {
      filter: 'Focus on key issues by status and severity',
      list: 'records total, sorted by CR Number (DESC)'
    },
    metricsMeta: {
      total: 'Issue records across the full lifecycle',
      analysis: 'Open and analysis-state CRs',
      other: 'CRs outside fixed/analysis rules',
      fixed: 'In Progress / Build / Closed / Duplicate'
    },
    placeholders: {
      all: 'All',
      optionalCrNumber: 'Optional: from CSV CR Number',
      noFrKeyword: 'Manual link if no FR keyword',
      optionalManualLink: 'Optional manual link',
      createdOnFormat: 'MM/DD/YYYY h:mm:ss AM',
      softwareBuild: 'Software Image Integration Build'
    },
    toast: {
      loadFailed: 'Failed to load data',
      noDataToExport: 'No data to export',
      exportSuccessPrefix: 'Exported top',
      exportSuccessSuffix: 'records',
      exportFailed: 'Failed to export data',
      importFailed: 'Failed to import CSV bugs',
      updateSuccess: 'Updated successfully',
      createSuccess: 'Created successfully',
      saveFailed: 'Failed to save',
      deleteConfirmTitle: 'Confirm',
      deleteConfirmContent: 'Are you sure you want to delete this bug?',
      deleteSuccess: 'Deleted successfully',
      deleteFailed: 'Failed to delete'
    }
  },
  testProgress: {
    hero: 'Review task status, case pass results, and team collaboration in one place so delivery pace and risk exposure stay visible.',
    sectionMeta: {
      overview: 'Aggregate passed, failed, and untested cases across all tasks to quickly gauge current execution health.',
      list: 'Review current execution status by status, pass rate, and ownership.'
    },
    metricsMeta: {
      total: 'All test tasks included in the current view',
      running: 'Tests currently in execution',
      completed: 'Delivered and completed test items',
      passRate: 'Overall pass performance from the current list'
    },
    placeholders: {
      frExample: 'Example: FR-2026-001',
      testName: 'Enter the test name',
      featureSummary: 'Briefly describe the FR feature',
      detailDescription: 'Detailed description of the feature',
      configMethod: 'How the feature is configured',
      testers: 'Multiple selection supported, new names allowed',
      developers: 'Separate multiple names with commas, e.g. Alice, Bob',
      l0DueDate: 'Select the L0 due date',
      l2DueDate: 'Select the L2 due date',
      l4DueDate: 'Select the L4 due date'
    },
    helper: {
      inputFormat: 'Input format: Pass / Fail / Total (Untested = Total - Pass - Fail, not counted as failures)',
      autoProgressPrefix: 'Calculated automatically',
      dueDatePrefix: 'Due Date:'
    },
    toast: {
      loadFailed: 'Failed to load data',
      updateSuccess: 'Updated successfully',
      createSuccess: 'Created successfully',
      saveFailed: 'Failed to save'
    }
  },
  testDetail: {
    hero: 'Review one test task in depth, including feature notes, configuration, current status, progress breakdown, and linked defects for follow-up and handoff.',
    sectionMeta: {
      featureConfig: 'Capture task background, feature details, and configuration notes for tracking and handoff.',
      stageStats: 'Each stage is shown as Pass/Fail/Total, and untested cases are not counted as failures.',
      linkedBugs: 'An overview of linked issues and their processing state.'
    },
    metricsMeta: {
      currentProgress: 'Calculated automatically from passed cases',
      passedTotal: 'Includes all L0 / L2 / L4 statistics',
      linkedBugs: 'Issues currently linked to this test task',
      estimatedManday: 'Shown on the detail page only'
    },
    tableEmptyBugs: 'No linked bugs',
    toast: {
      loadFailed: 'Failed to load details'
    }
  },
  personnel: {
    hero: 'Personnel data is injected by the backend. This page focuses on task completion, manday allocation, and overlap risk across the L0 to L4 time window.',
    sectionMeta: 'Expand to view task details and overlap information',
    metricsMeta: {
      members: 'Active test members',
      avgTasks: 'Average based on current members',
      totalManday: 'Summed from task manday allocations',
      overlapGroups: 'Overlapping pairs in the L0-L4 window'
    },
    placeholders: {
      selectMember: 'Select a member',
      partDescriptionExample: 'Example: login module regression + API smoke tests'
    },
    fallback: {
      unassignedPart: '-'
    },
    toast: {
      loadFailed: 'Failed to load personnel data',
      loadTaskAllocationsFailed: 'Failed to load task allocations',
      duplicateTester: 'The same tester cannot be assigned more than once',
      saveSuccess: 'Manday allocation updated',
      saveFailed: 'Failed to save allocation'
    }
  },
  personnelDetail: {
    hero: 'Review one member\'s assignments, schedule span, progress, and manday distribution.',
    sectionMeta: {
      profile: 'Basic member identity and permission info.',
      tasks: 'Unified task list including test tasks and work tasks.'
    },
    fallback: {
      unassignedPart: '-'
    },
    toast: {
      loadFailed: 'Failed to load member detail'
    }
  },
  kpi: {
    hero: 'Compare model performance through a modern visualization surface to spot leading models, key changes, and trade-offs across metrics.',
    scope: 'Current Scope: all models in the selected category',
    categoryCurrentPrefix: 'Current category:',
    categoryCurrentSuffix: 'The charts compare all models within this category only.',
    modelInfoHint: 'Click a model in the ladder chart to sync the information shown here.',
    sectionMeta: {
      ladder: 'Vertical ranking of models in the same category under one core metric.',
      scatter: 'Observe the trade-offs and distribution between two core metrics for models in the same category.'
    },
    scatterHint: 'Two metrics are selected by default; choosing a third removes the earliest selected metric.',
    placeholders: {
      selectModelA: 'Select Model A',
      selectModelB: 'Select Model B',
      compareEmpty: 'Select two different models to compare'
    }
  },
  workTasks: {
    hero: 'Manage customer support, automation development, and other work items in one place with direct personnel assignment.',
    sectionMeta: {
      list: 'Filter by type, status, assignee, and keyword'
    },
    metricsMeta: {
      planned: 'Tasks waiting to start',
      inProgress: 'Tasks currently being executed',
      completed: 'Closed work items',
      paused: 'Currently blocked tasks'
    },
    placeholders: {
      search: 'Search by task name, summary, or detail',
      taskType: 'Task Type',
      taskStatus: 'Task Status',
      assignee: 'Assignee',
      taskKeyExample: 'Example: CS-20260316-001',
      selectType: 'Select a type',
      taskName: 'Enter the task name',
      selectStatus: 'Select a status',
      optional: 'Optional'
    },
    toast: {
      loadFailed: 'Failed to load tasks',
      taskKeyRequired: 'Task key cannot be empty',
      taskNameRequired: 'Task name cannot be empty',
      taskTypeRequired: 'Please select a task type',
      taskStatusRequired: 'Please select a task status',
      invalidDateRange: 'End date cannot be earlier than start date',
      updateSuccess: 'Task updated successfully',
      createSuccess: 'Task created successfully',
      saveFailed: 'Failed to save task',
      deleteConfirmTitle: 'Delete Confirmation',
      deleteConfirmPrefix: 'Delete task',
      deleteConfirmSuffix: '?',
      deleteSuccess: 'Task deleted',
      deleteFailed: 'Failed to delete task'
    }
  },
  workTaskDetail: {
    hero: 'Review task ownership, status, schedule, and detailed description for tracking and collaboration.',
    sectionMeta: {
      basicInfo: 'Core tracking fields for this task.',
      detail: 'Detailed task content and context.'
    },
    fallback: {
      noSummary: 'No task summary',
      noDetail: 'No task detail',
      unassigned: 'Unassigned'
    },
    toast: {
      loadFailed: 'Failed to load task details'
    }
  }
}

export default DescriptionText
