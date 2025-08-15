import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { UserCircle, Menu, X } from "lucide-react";

export default function Navbar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Agents", path: "/agents" },
  ];

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">

          {/* Logo & Links */}
          <div className="flex items-center">
            <Link
              to="/"
              className="text-2xl font-semibold text-gray-900 tracking-tight"
            >
              Agent Central
            </Link>

            {/* Desktop Nav */}
            <nav className="ml-8 space-x-6 hidden md:flex">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`transition-colors duration-200 ${location.pathname === link.path
                      ? "text-blue-600 font-medium border-b-2 border-blue-600 pb-1"
                      : "text-gray-700 hover:text-blue-600"
                    }`}
                >
                  {link.name}
                </Link>
              ))}
            </nav>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center gap-3 bg-gray-50 px-3 py-1 rounded-full shadow-sm hover:shadow-md transition">
                <div className="w-10 h-10 rounded-full overflow-hidden bg-gray-200 flex items-center justify-center">
                  {user?.avatarUrl ? (
                    <img src={user.avatarUrl} alt="User Avatar" className="w-full h-full object-cover" />
                  ) : (
                    <UserCircle className="w-8 h-8 text-gray-600" />
                  )}
                </div>

                <span className="text-sm text-gray-800 max-w-[120px] truncate">
                  {user.displayName || user.email}
                </span>
                <button
                  onClick={async () => {
                    await signOut();
                    navigate("/");
                  }}
                  className="px-3 py-1 text-xs bg-red-500 text-white rounded-full hover:bg-red-600 transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/auth"
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 transition"
              >
                Login / Register
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-md hover:bg-gray-100 transition"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white shadow-lg">
          <nav className="px-4 py-4 space-y-3">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsMenuOpen(false)}
                className={`block transition-colors duration-200 ${location.pathname === link.path
                    ? "text-blue-600 font-medium"
                    : "text-gray-700 hover:text-blue-600"
                  }`}
              >
                {link.name}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
