import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { useApi } from '../hooks/useApi';
import { mockOneOnOnes, mockEmployee, mockEmployeeSkills } from '../mocks/data';

const Section = ({ title, children }) => (
  <section className="panel">
    <header className="panel-header">
      <h2>{title}</h2>
    </header>
    {children}
  </section>
);

export default function EmployeeProfile() {
  const { employeeUid } = useParams();
  const { fetchJson } = useApi();
  const [employee, setEmployee] = useState(null);
  const [skills, setSkills] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [profile, employeeSkills, oneOnOnes] = await Promise.all([
          fetchJson(`/employees/${employeeUid}`),
          fetchJson(`/skills/assignments/${employeeUid}`),
          fetchJson(`/one-on-ones/employees/${employeeUid}?limit=5`)
        ]);
        if (active) {
          setEmployee(profile);
          setSkills(employeeSkills);
          setTimeline(oneOnOnes);
        }
      } catch (error) {
        console.warn('Using mock data for employee profile');
        if (active) {
          setEmployee(mockEmployee(employeeUid));
          setSkills(mockEmployeeSkills(employeeUid));
          setTimeline(mockOneOnOnes);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      active = false;
    };
  }, [fetchJson, employeeUid]);

  if (loading) {
    return <div className="panel">Loading profile...</div>;
  }

  if (!employee) {
    return <div className="panel">Employee not found.</div>;
  }

  return (
    <div className="profile-grid">
      <Section title="Overview">
        <div className="profile-summary">
          <div>
            <h3>
              {employee.firstName} {employee.lastName}
            </h3>
            <p>{employee.title}</p>
            <p>{employee.department}</p>
            <p>{employee.email}</p>
          </div>
          <div>
            <p>Manager: {employee.managerUid || 'N/A'}</p>
            <p>Status: {employee.status}</p>
          </div>
        </div>
      </Section>

      <Section title="Skills & Expertise">
        {skills.length === 0 ? (
          <p>No skills recorded yet.</p>
        ) : (
          <div className="skills-grid">
            {skills.map((skill) => (
              <div key={skill.uid} className="skill-pill">
                <div>
                  <strong>{skill.skillName}</strong>
                  <p>Level {skill.level}</p>
                </div>
                <span className="skill-source">{skill.source}</span>
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section title="Recent 1:1s">
        {timeline.length === 0 ? (
          <p>No 1:1 history.</p>
        ) : (
          <ul className="timeline">
            {timeline.map((entry) => (
              <li key={entry.session.uid}>
                <div className="timeline-header">
                  <h3>{entry.session.sessionDate}</h3>
                  <p>{entry.session.agenda || 'General sync'}</p>
                </div>
                <div className="timeline-body">
                  <h4>Notes</h4>
                  {entry.notes.length === 0 ? (
                    <p>No shared notes.</p>
                  ) : (
                    entry.notes.map((note) => (
                      <p key={note.uid} className="note">
                        {note.content}
                      </p>
                    ))
                  )}
                  <h4>Action items</h4>
                  {entry.actionItems.length === 0 ? (
                    <p>No open actions.</p>
                  ) : (
                    entry.actionItems.map((action) => (
                      <div key={action.uid} className="action-row">
                        <p>{action.description}</p>
                        <span className={`status ${action.status.toLowerCase()}`}>
                          {action.status}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Section>
    </div>
  );
}

