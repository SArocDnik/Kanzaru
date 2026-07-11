import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import Layout from "./components/Layout"
import ProjectList from "./components/ProjectList"
import UploadPanel from "./components/UploadPanel"
import ChapterList from "./components/ChapterList"
import ChapterDetail from "./components/ChapterDetail"

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<ProjectList />} />
            <Route path="/upload" element={<UploadPanel />} />
            <Route path="/projects/:id" element={<ChapterList />} />
            <Route path="/projects/:id/chapters/:chapterId" element={<ChapterDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
