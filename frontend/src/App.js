import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "@/pages/Dashboard";
import MatchDetail from "@/pages/MatchDetail";
import { Toaster } from "@/components/ui/sonner";

function App() {
  return (
    <div className="App dark">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/match/:matchId" element={<MatchDetail />} />
        </Routes>
      </BrowserRouter>
      <Toaster theme="dark" />
    </div>
  );
}

export default App;