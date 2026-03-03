import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, Users, TrendingUp, FileText } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Upload', icon: FileText },
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/trades', label: 'Trade Analysis', icon: TrendingUp },
    { path: '/contracts', label: 'Contracts', icon: Users },
  ];
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <BarChart3 className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                Apex Zero
              </span>
            </div>
          </div>
          
          {/* Navigation Links */}
          <div className="flex items-center space-x-4">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive(path)
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="h-4 w-4 mr-1.5" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
