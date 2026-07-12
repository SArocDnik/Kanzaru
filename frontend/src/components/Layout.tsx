import { Outlet, NavLink } from "react-router-dom"

const navItems = [
  { to: "/", label: "Projects" },
  { to: "/upload", label: "Upload" },
]

export default function Layout() {
  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col">
        <h1 className="text-xl font-bold px-6 py-4 border-b border-slate-700">Kanzaru</h1>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `block px-4 py-2 rounded transition-colors ${
                  isActive ? "bg-slate-700 text-white" : "text-slate-300 hover:bg-slate-800"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto bg-slate-50 p-6">
        <Outlet />
      </main>
    </div>
  )
}
