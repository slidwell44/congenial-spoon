export const mockOrgTree = {
  root: {
    employee: {
      uid: '11111111-1111-1111-1111-111111111111',
      firstName: 'Riley',
      lastName: 'Manager',
      title: 'Engineering Manager',
      department: 'Engineering'
    },
    summary: {
      totalReports: 3,
      managerCount: 1,
      icCount: 2,
      openRoles: 1
    },
    directReports: [
      {
        employee: {
          uid: '22222222-2222-2222-2222-222222222222',
          firstName: 'Sam',
          lastName: 'Lead',
          title: 'Tech Lead',
          department: 'Platform'
        },
        summary: { totalReports: 2, managerCount: 0, icCount: 2, openRoles: 0 },
        directReports: [
          {
            employee: {
              uid: '33333333-3333-3333-3333-333333333333',
              firstName: 'Ivy',
              lastName: 'Engineer',
              title: 'Senior Engineer',
              department: 'Platform'
            },
            summary: { totalReports: 0, managerCount: 0, icCount: 0, openRoles: 0 },
            directReports: []
          }
        ]
      }
    ]
  }
};

export const mockSkillMatrix = {
  rows: [
    {
      employeeUid: '33333333-3333-3333-3333-333333333333',
      employeeName: 'Ivy Engineer',
      title: 'Senior Engineer',
      skills: [
        {
          skillUid: '44444444-4444-4444-4444-444444444444',
          skillName: 'Python',
          level: 4,
          source: 'MANAGER',
          lastUpdatedBy: '1111',
          lastUpdatedAt: new Date().toISOString()
        }
      ]
    }
  ]
};

export const mockOneOnOnes = [
  {
    session: {
      uid: '55555555-5555-5555-5555-555555555555',
      sessionDate: '2025-01-15',
      agenda: 'Career growth',
      managerUid: '1111',
      employeeUid: '33333333-3333-3333-3333-333333333333'
    },
    notes: [
      {
        uid: '6666',
        content: 'Discussed promotion path',
        visibility: 'SHARED',
        createdAt: new Date().toISOString()
      }
    ],
    actionItems: [
      {
        uid: '7777',
        description: 'Draft growth plan',
        status: 'IN_PROGRESS'
      }
    ]
  }
];

export const mockEmployee = (uid) => {
  const employees = {
    '11111111-1111-1111-1111-111111111111': {
      uid: '11111111-1111-1111-1111-111111111111',
      firstName: 'Riley',
      lastName: 'Manager',
      title: 'Engineering Manager',
      department: 'Engineering',
      email: 'riley.manager@example.com',
      managerUid: null,
      status: 'ACTIVE'
    },
    '22222222-2222-2222-2222-222222222222': {
      uid: '22222222-2222-2222-2222-222222222222',
      firstName: 'Sam',
      lastName: 'Lead',
      title: 'Tech Lead',
      department: 'Platform',
      email: 'sam.lead@example.com',
      managerUid: '11111111-1111-1111-1111-111111111111',
      status: 'ACTIVE'
    },
    '33333333-3333-3333-3333-333333333333': {
      uid: '33333333-3333-3333-3333-333333333333',
      firstName: 'Ivy',
      lastName: 'Engineer',
      title: 'Senior Engineer',
      department: 'Platform',
      email: 'ivy.engineer@example.com',
      managerUid: '22222222-2222-2222-2222-222222222222',
      status: 'ACTIVE'
    }
  };
  return employees[uid] || {
    uid,
    firstName: 'Unknown',
    lastName: 'Employee',
    title: 'N/A',
    department: 'N/A',
    email: 'unknown@example.com',
    managerUid: null,
    status: 'ACTIVE'
  };
};

export const mockEmployeeSkills = (uid) => {
  const skillsByEmployee = {
    '33333333-3333-3333-3333-333333333333': [
      {
        uid: '44444444-4444-4444-4444-444444444444',
        skillName: 'Python',
        level: 4,
        source: 'MANAGER',
        lastUpdatedBy: '11111111-1111-1111-1111-111111111111',
        lastUpdatedAt: new Date().toISOString()
      },
      {
        uid: '88888888-8888-8888-8888-888888888888',
        skillName: 'React',
        level: 3,
        source: 'SELF',
        lastUpdatedBy: '33333333-3333-3333-3333-333333333333',
        lastUpdatedAt: new Date().toISOString()
      }
    ]
  };
  return skillsByEmployee[uid] || [];
};

