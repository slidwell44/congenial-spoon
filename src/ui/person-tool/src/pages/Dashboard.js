import { useContext, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { CurrentUserContext } from '../context/CurrentUserContext';
import { useApi } from '../hooks/useApi';
import { mockOrgTree } from '../mocks/data';

const SummaryCard = ({ label, value }) => (
  <div className="summary-card">
    <p className="summary-label">{label}</p>
    <p className="summary-value">{value}</p>
  </div>
);

const OrgNode = ({ node }) => (
  <li>
    <div className="org-node">
      <div>
        <p className="org-name">
          {node.employee.firstName} {node.employee.lastName}
        </p>
        <p className="org-title">{node.employee.title}</p>
      </div>
      <Link to={`/employees/${node.employee.uid}`}>View profile</Link>
    </div>
    {node.directReports && node.directReports.length > 0 && (
      <ul>
        {node.directReports.map((child) => (
          <OrgNode key={child.employee.uid} node={child} />
        ))}
      </ul>
    )}
  </li>
);

export default function Dashboard() {
  const user = useContext(CurrentUserContext);
  const { fetchJson } = useApi();
  const [orgData, setOrgData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const data = await fetchJson(`/employees/${user.uid}/org?depth=3`);
        if (active) {
          setOrgData(data);
        }
      } catch (error) {
        console.warn('Falling back to mock org tree');
        if (active) {
          setOrgData(mockOrgTree);
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

  const summary = useMemo(() => {
    if (!orgData) {
      return { totalReports: 0, managerCount: 0, icCount: 0, openRoles: 0 };
    }
    return orgData.root.summary;
  }, [orgData]);

  if (loading) {
    return <div className="panel">Loading your org...</div>;
  }

  if (!orgData) {
    return <div className="panel">No org data available.</div>;
  }

  return (
    <div className="dashboard-grid">
      <section className="panel">
        <header className="panel-header">
          <h2>My Org Snapshot</h2>
        </header>
        <div className="summary-grid">
          <SummaryCard label="Total reports" value={summary.totalReports} />
          <SummaryCard label="Managers" value={summary.managerCount} />
          <SummaryCard label="ICs" value={summary.icCount} />
          <SummaryCard label="Open roles" value={summary.openRoles ?? 0} />
        </div>
      </section>

      <section className="panel">
        <header className="panel-header">
          <h2>Org Tree</h2>
        </header>
        <ul className="org-tree">
          <OrgNode node={orgData.root} />
        </ul>
      </section>

      <section className="panel">
        <header className="panel-header">
          <h2>Next Actions</h2>
          <p>Stay on top of follow-ups and 1:1 cadences.</p>
        </header>
        <div className="action-grid">
          <div className="action-card">
            <h3>Schedule overdue 1:1s</h3>
            <p>3 direct reports have not met in the past 4 weeks.</p>
            <Link to={`/one-on-ones`}>Review timeline</Link>
          </div>
          <div className="action-card">
            <h3>Review skill gaps</h3>
            <p>Platform team missing Kafka expertise for Q1 launch.</p>
            <Link to="/skills-matrix">Open skills matrix</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
