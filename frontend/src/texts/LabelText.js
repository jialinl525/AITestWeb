export const LabelText = {
  app: {
    brandSubtitle: 'Test Management Dashboard',
    navigation: 'Navigation',
    currentRole: 'Current Role',
    editableTest: 'Editable Test',
    readOnly: 'Read Only',
    workbenchStatus: 'Workbench Status',
    online: 'Online',
    headerTitle: 'Quality Operations Overview',
    headerSubtitle: 'Get clear insight into test progress, defect status, and model performance',
    guestMode: 'Guest Mode',
    canEditTests: 'Can Edit Tests',
    roleMap: {
      manager: 'Manager',
      viewer: 'Viewer'
    },
    menu: {
      testProgress: 'FR Progress',
      workTasks: 'Task',
      bugs: 'CR Tracking',
      personnel: 'Personnel',
      kpi: 'Model Ladder'
    },
    form: {
      username: 'Username',
      password: 'Password',
      currentPassword: 'Current Password',
      newPassword: 'New Password',
      confirmNewPassword: 'Confirm New Password'
    }
  },
  bugs: {
    heroEyebrow: 'Risk Tracking',
    heroTitle: 'Bug Risk Tracking Dashboard',
    testFilterLabel: 'Current Test ID Filter',
    section: {
      filterTitle: 'Filter and Search',
      listTitle: 'Bug List'
    },
    filter: {
      status: 'Status',
      createdBy: 'Created By'
    },
    metrics: {
      total: 'Total Bugs',
      analysis: 'Analysis',
      other: 'Other',
      fixed: 'Fixed'
    },
    table: {
      crNumber: 'CR Number',
      title: 'Title',
      status: 'Status',
      createdBy: 'Created By',
      crAssignee: 'CR Assignee',
      createdOn: 'Created On',
      build: 'Software Image Integration Build',
      actions: 'Actions'
    },
    dialog: {
      exportTopNTitle: 'Export Top N Bugs',
      rowsToExport: 'Rows to export',
      editTitle: 'Edit Bug',
      newTitle: 'New Bug'
    },
    form: {
      crNumber: 'CR Number',
      testTask: 'Test Task',
      workTask: 'WorkTask',
      title: 'Title',
      createdBy: 'Created By',
      crAssignee: 'CR Assignee',
      createdOn: 'Created On',
      build: 'Build',
      status: 'Status'
    },
    statusOptions: {
      fixed: 'Fixed',
      analysis: 'Analysis',
      other: 'Other',
      verified: 'Verified',
      discarded: 'Discarded'
    }
  },
  testProgress: {
    heroEyebrow: 'Test Operations',
    heroTitle: 'Test Progress Overview',
    pills: {
      testTasks: 'Test Tasks',
      averageProgress: 'Average Progress'
    },
    inline: {
      totalCases: 'Total Cases',
      records: 'Records'
    },
    overviewTitle: 'Overall Test Progress Distribution',
    listTitle: 'Test Task List',
    metrics: {
      total: 'Total Tests',
      running: 'Running',
      completed: 'Completed',
      passRate: 'Case Pass Rate'
    },
    summary: {
      passed: 'Passed',
      failed: 'Failed',
      untested: 'Untested'
    },
    table: {
      taskInfo: 'Task Info',
      risk: 'Risk',
      status: 'Status',
      l0: 'L0',
      l2: 'L2',
      l4: 'L4',
      total: 'Total',
      progress: 'Progress',
      testers: 'Testers',
      actions: 'Actions'
    },
    dialog: {
      editTitle: 'Edit Test',
      newTitle: 'New Test'
    },
    form: {
      frNumber: 'FR Number',
      testName: 'Test Name',
      featureSummary: 'Feature Summary',
      detailedDescription: 'Detailed Description',
      configMethod: 'Configuration Method',
      testers: 'Testers',
      developers: 'Developers',
      status: 'Status',
      l0Cases: 'L0 Cases',
      l0DueDate: 'L0 Due Date',
      l2Cases: 'L2 Cases',
      l2DueDate: 'L2 Due Date',
      l4Cases: 'L4 Cases',
      l4DueDate: 'L4 Due Date',
      progress: 'Progress'
    },
    statusText: {
      pending: 'Pending',
      running: 'Running',
      completed: 'Completed',
      failed: 'Failed'
    },
    riskText: {
      overdue: 'Overdue',
      atRisk: 'At Risk',
      normal: 'Normal'
    }
  },
  testDetail: {
    heroEyebrow: 'Task Detail',
    heroTitle: 'Test Task Details',
    status: 'Status',
    createdOn: 'Created on',
    noFeatureSummary: 'No feature summary yet',
    metrics: {
      currentProgress: 'Current Progress',
      passedTotal: 'Passed / Total Cases',
      linkedBugs: 'Linked Bugs',
      estimatedManday: 'Estimated Manday'
    },
    people: {
      frNumber: 'FR Number',
      testers: 'Testers',
      developers: 'Developers'
    },
    section: {
      featureConfig: 'Feature and Configuration',
      stageStats: 'Stage Statistics and Task Status',
      linkedBugs: 'Linked Bugs'
    },
    info: {
      featureSummary: 'Feature Summary (FR Brief)',
      frNumber: 'FR Number',
      detailedDescription: 'Detailed Description',
      configMethod: 'Configuration Method',
      status: 'Status',
      testers: 'Testers',
      developers: 'Developers',
      estimatedManday: 'Estimated Manday',
      startDate: 'Start Date',
      completionDate: 'Completion Date',
      l0: 'L0 (Pass/Fail/Total)',
      l0DueDate: 'L0 Due Date',
      l2: 'L2 (Pass/Fail/Total)',
      l2DueDate: 'L2 Due Date',
      l4: 'L4 (Pass/Fail/Total)',
      l4DueDate: 'L4 Due Date',
      overall: 'Overall (Pass/Fail/Total)',
      progress: 'Progress',
      createdAt: 'Created At',
      updatedAt: 'Updated At'
    },
    table: {
      crNumber: 'CR Number',
      title: 'Title',
      status: 'Status',
      createdBy: 'Created By',
      crAssignee: 'CR Assignee',
      createdOn: 'Created On',
      build: 'Software Image Integration Build'
    },
    statusText: {
      pending: 'Pending',
      running: 'Running',
      completed: 'Completed',
      failed: 'Failed'
    },
    bugStatusText: {
      fixed: 'Fixed',
      analysis: 'Analysis',
      other: 'Other'
    }
  },
  personnel: {
    heroEyebrow: 'People Dashboard',
    heroTitle: 'Personnel Task and Manday Dashboard',
    pills: {
      members: 'Members',
      tasks: 'Tasks',
      mandays: 'Mandays',
      overlaps: 'Overlaps'
    },
    metrics: {
      members: 'Members',
      avgTasks: 'Avg. Tasks per Member',
      totalManday: 'Total Allocated Mandays',
      overlapGroups: 'Overlap Groups'
    },
    sectionTitle: 'Task Completion and Manday Allocation by Member',
    table: {
      task: 'Task',
      partDescription: 'Work Part',
      startDate: 'Start Date',
      endDate: 'End Date',
      status: 'Status',
      progress: 'Progress',
      allocatedManday: 'Manday',
      actions: 'Actions',
      member: 'Member',
      username: 'Username',
      taskCount: 'Task Count',
      completedTasks: 'Completed Tasks',
      overlapGroups: 'Overlap Groups'
    },
    overlaps: {
      title: 'Date Overlaps (L0 to L4 Window)',
      noOverlaps: 'No overlaps',
      taskA: 'Task A',
      taskB: 'Task B',
      overlapRange: 'Overlap Range',
      overlapDays: 'Overlap Days'
    },
    dialog: {
      taskMandayAllocation: 'Task Manday Allocation',
      totalTaskManday: 'Total Task Manday',
      tester: 'Tester',
      allocatedManday: 'Allocated Manday',
      partDescription: 'Part Description',
      actions: 'Actions'
    }
  },
  personnelDetail: {
    heroEyebrow: 'Member Detail',
    heroTitle: 'Personnel Detail',
    metrics: {
      taskCount: 'Task Count',
      completedTasks: 'Completed Tasks',
      overlapGroups: 'Overlap Groups',
      totalManday: 'Total Manday'
    },
    section: {
      profile: 'Member Profile',
      tasks: 'Task List'
    },
    profile: {
      displayName: 'Display Name',
      username: 'Username',
      editable: 'Editable'
    }
  },
  kpi: {
    heroEyebrow: 'Model Performance',
    heroTitle: 'KPI Smart Analytics Dashboard',
    category: {
      eyebrow: 'Model Category',
      title: 'Model Category Filter',
      current: 'Current'
    },
    modelInfo: {
      title: 'Model Information',
      modelCategory: 'Model Category',
      currentMetric: 'Current Metric',
      description: 'Description',
      source: 'Source',
      modelSize: 'Model Size',
      power: 'Power Consumption',
      latency: 'Latency',
      accuracy: 'Accuracy'
    },
    section: {
      ladder: 'Model Performance Ladder',
      scatter: 'Model Performance Scatter Plot'
    },
    compare: {
      title: 'Model Comparison',
      parameter: 'Parameter',
      modelA: 'Model A',
      modelB: 'Model B'
    }
  },
  workTasks: {
    heroEyebrow: 'Unified Task Board',
    heroTitle: 'Customer Support / Automation Development Task Management',
    pills: {
      totalTasks: 'Total Tasks',
      totalManday: 'Total Manday',
      inProgress: 'In Progress'
    },
    metrics: {
      planned: 'Planned',
      inProgress: 'In Progress',
      completed: 'Completed',
      paused: 'Paused'
    },
    sectionTitle: 'Task List',
    table: {
      key: 'Key',
      taskType: 'Task Type',
      taskName: 'Task Name',
      taskSummary: 'Task Summary',
      taskDetail: 'Task Detail',
      startDate: 'Start Date',
      endDate: 'End Date',
      estimatedManday: 'Estimated Manday',
      status: 'Status',
      progress: 'Progress',
      assignee: 'Assignee',
      actions: 'Actions'
    },
    form: {
      taskKey: 'Task Key',
      taskType: 'Task Type',
      taskName: 'Task Name',
      taskSummary: 'Task Summary',
      taskDetail: 'Task Detail',
      startDate: 'Start Date',
      endDate: 'End Date',
      estimatedManday: 'Estimated Manday',
      progress: 'Progress',
      status: 'Status',
      assignee: 'Assignee'
    },
    dialog: {
      editTitle: 'Edit Task',
      newTitle: 'New Task'
    }
  },
  workTaskDetail: {
    heroEyebrow: 'Task Detail',
    heroTitle: 'Work Task Details',
    metrics: {
      status: 'Status',
      type: 'Task Type',
      progress: 'Progress',
      assignee: 'Assignee',
      estimatedManday: 'Estimated Manday'
    },
    section: {
      basicInfo: 'Task Basic Information',
      detail: 'Task Description'
    },
    info: {
      taskName: 'Task Name',
      taskType: 'Task Type',
      taskSummary: 'Task Summary',
      startDate: 'Start Date',
      endDate: 'End Date',
      status: 'Status',
      progress: 'Progress',
      assignee: 'Assignee',
      estimatedManday: 'Estimated Manday',
      createdAt: 'Created At',
      updatedAt: 'Updated At',
      taskDetail: 'Task Detail'
    }
  }
}

export default LabelText
