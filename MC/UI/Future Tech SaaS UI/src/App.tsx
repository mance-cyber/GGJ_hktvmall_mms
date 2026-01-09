import { useState } from 'react';
import { Dashboard } from './components/Dashboard';

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <Dashboard />
    </div>
  );
}