import { useState, useEffect } from "react";
import "./App.css";
import Navbar from "./components/navbar.jsx";
import { Route, Routes, useLocation } from "react-router-dom";
import NewChapters from "./pages/NewChapters.jsx";
import SavedManga from "./pages/SavedManga.jsx";
import ReReads from "./pages/ReReads.jsx";
import Login from "./pages/Login.jsx";
import SignUp from "./pages/SignUp.jsx";
import { API_URL } from "./config/index.js";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY,
);

function App() {
  const [newChapters, setNewChapters] = useState([]);
  const [savedManga, setSavedManga] = useState([]);
  const [reReads, setReReads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dataFetched, setDataFetched] = useState(false); // Track if data has been fetched
  const location = useLocation();

  useEffect(() => {
    async function fetchAllData() {
      try {
        setLoading(true);
        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession();

        if (sessionError || !session) {
          console.log("No active session");
          setLoading(false);
          return;
        }

        const token = session.access_token;

        const [newChaptersRes, savedMangaRes, reReadsRes] = await Promise.all([
          fetch(`${API_URL}get-new-chapters`, {
            headers: {
              "Content-Type": "application/json; charset=UTF-8",
              Authorization: `Bearer ${token}`,
            },
          }),
          fetch(`${API_URL}get-saved-manga`, {
            headers: {
              "Content-Type": "application/json; charset=UTF-8",
              Authorization: `Bearer ${token}`,
            },
          }),
          fetch(`${API_URL}get-re-reads`, {
            headers: {
              "Content-Type": "application/json; charset=UTF-8",
              Authorization: `Bearer ${token}`,
            },
          }),
        ]);

        const [newChaptersData, savedMangaData, reReadsData] =
          await Promise.all([
            newChaptersRes.json(),
            savedMangaRes.json(),
            reReadsRes.json(),
          ]);

        console.log("newChaptersData", newChaptersData);
        console.log("savedMangaData", savedMangaData);
        console.log("reReadsData", reReadsData);

        setNewChapters(newChaptersData.new_chapters || []);
        setSavedManga(savedMangaData.saved_manga || []);
        setReReads(reReadsData.re_reads || []);
        setDataFetched(true);

        console.log("Fetched all data:", {
          newChaptersData,
          savedMangaData,
          reReadsData,
        });
      } catch (err) {
        console.error("Failed to fetch data:", err);
      } finally {
        setLoading(false);
      }
    }

    const justLoggedIn = location.state?.justLoggedIn;
    const isProtectedRoute =
      location.pathname !== "/" && location.pathname !== "/sign-up";

    // Fetch on mount if on protected route, or when justLoggedIn changes
    if (isProtectedRoute && !dataFetched) {
      fetchAllData();
    }
  }, [location.pathname, dataFetched]); // Remove location.state from dependencies

  return (
    <div className="min-h-screen pt-15 px-10">
      {location.pathname !== "/" && location.pathname !== "/sign-up" && (
        <div className="flex items-center justify-between">
          <Navbar />
        </div>
      )}

      <div className="container">
        {loading ? (
          <div className="flex items-center justify-center h-screen">
            <p className="text-xl">Loading...</p>
          </div>
        ) : (
          <Routes>
            <Route path="" element={<Login />} />
            <Route path="/sign-up" element={<SignUp />} />
            <Route
              path="/new-chapters"
              element={<NewChapters data={newChapters} />}
            />
            <Route
              path="/saved-manga"
              element={<SavedManga data={savedManga} />}
            />
            <Route path="/re-reads" element={<ReReads data={reReads} />} />
          </Routes>
        )}
      </div>
    </div>
  );
}

export default App;
