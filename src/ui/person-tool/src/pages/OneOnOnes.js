import { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { CurrentUserContext } from '../context/CurrentUserContext';
import { useApi } from '../hooks/useApi';
import { mockOneOnOnes } from '../mocks/data';

const Section = ({ title, children }) => (
  <section className="panel">
    <header className="panel-header">
      <h2>{title}</h2>
    </header>
    {children}
  </section>
);

export default function OneOnOnes() {
  const user = useContext(CurrentUserContext);
  const { fetchJson } = useApi();
  const [oneOnOnes, setOneOnOnes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const data = await fetchJson(`/one-on-ones?managerUid=${user.uid}&limit=20`);
        if (active) {
          setOneOnOnes(data);
        }
      } catch (error) {
        console.warn('Using mock data for 1:1s');
        if (active) {
          setOneOnOnes(mockOneOnOnes);
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
    return <div className="panel">Loading 1:1s...</div>;
  }

  if (oneOnOnes.length === 0) {
    return (
      <Section title="1:1 Meetings">
        <p>No 1:1 meetings found. Schedule your first 1:1 with a direct report.</p>
      </Section>
    );
  }

  return (
    <Section title="1:1 Meetings">
      <p>Recent and upcoming 1:1s with your direct reports.</p>
      <ul className="timeline">
        {oneOnOnes.map((entry) => (
          <li key={entry.session.uid}>
            <div className="timeline-header">
              <h3>
                <Link to={`/employees/${entry.session.employeeUid}`}>
                  Employee Profile
                </Link>
              </h3>
              <p>
                <strong>Date:</strong> {entry.session.sessionDate}
              </p>
              <p>
                <strong>Agenda:</strong> {entry.session.agenda || 'General sync'}
              </p>
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
    </Section>
  );
}

