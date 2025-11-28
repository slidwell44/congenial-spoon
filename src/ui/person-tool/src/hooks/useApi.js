import { useContext } from 'react';

import { CurrentUserContext } from '../context/CurrentUserContext';

const API_BASE =
  process.env.REACT_APP_API_BASE || 'http://localhost:8000/api/v1';

export function useApi() {
  const user = useContext(CurrentUserContext);

  const fetchJson = async (path, options = {}) => {
    try {
      const response = await fetch(`${API_BASE}${path}`, {
        headers: {
          'Content-Type': 'application/json',
          'X-User-Uid': user.uid,
          'X-User-Role': user.role,
          ...(options.headers || {})
        },
        ...options
      });
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Request failed');
      }
      if (response.status === 204) {
        return null;
      }
      return await response.json();
    } catch (error) {
      console.warn('API error', error);
      throw error;
    }
  };

  return { fetchJson };
}

