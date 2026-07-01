import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ExercisesPage from "./pages/ExercisesPage";
import AthletesPage from "./pages/AthletesPage";
import PlanBuilderPage from "./pages/PlanBuilderPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/exercises" replace />} />
        <Route path="/exercises" element={<ExercisesPage />} />
        <Route path="/athletes" element={<AthletesPage />} />
        <Route path="/plans" element={<PlanBuilderPage />} />
        <Route path="*" element={<Navigate to="/exercises" replace />} />
      </Route>
    </Routes>
  );
}
