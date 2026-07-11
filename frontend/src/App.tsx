import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import Layout from "./components/Layout"

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Placeholder title="Projects" />} />
            <Route path="/upload" element={<Placeholder title="Upload" />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

function Placeholder({ title }: { title: string }) {
  return (
    <div>
      <h2 className="text-2xl font-bold text-slate-800">{title}</h2>
      <p className="mt-2 text-slate-500">Coming soon...</p>
    </div>
  )
}
