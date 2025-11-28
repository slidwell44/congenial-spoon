import { useContext, useEffect, useState } from 'react';

import { CurrentUserContext } from '../context/CurrentUserContext';
import { useApi } from '../hooks/useApi';
import { mockSkillMatrix } from '../mocks/data';

export default function SkillsMatrix() {
  const user = useContext(CurrentUserContext);
  const { fetchJson } = useApi();
  const [matrix, setMatrix] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const data = await fetchJson(`/skills/matrix?managerUid=${user.uid}`);
        if (active) {
          setMatrix(data);
        }
      } catch (error) {
        console.warn('Using mock skill matrix');
        if (active) {
          setMatrix(mockSkillMatrix);
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
  }, [fetchJson, user]);

  if (loading) {
    return <div className="panel">Loading skills matrix...</div>;
  }

  if (!matrix) {
    return <div className="panel">No skill data available.</div>;
  }

  return (
    <section className="panel">
      <header className="panel-header">
        <h2>Skills Matrix</h2>
        <p>Snapshot of your team&apos;s strengths and gaps.</p>
      </header>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Team member</th>
              <th>Role</th>
              <th>Skills</th>
            </tr>
          </thead>
          <tbody>
            {matrix.rows.map((row) => (
              <tr key={row.employeeUid}>
                <td>{row.employeeName}</td>
                <td>{row.title}</td>
                <td>
                  {row.skills.length === 0 ? (
                    <span className="empty-pill">No skills captured</span>
                  ) : (
                    row.skills.map((skill) => (
                      <span key={skill.skillUid} className="skill-pill inline">
                        {skill.skillName} (L{skill.level})
                      </span>
                    ))
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
