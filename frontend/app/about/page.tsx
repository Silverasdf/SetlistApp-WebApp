import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About | SetlistApp",
  description: "About SetlistApp, a local-first setlist builder for bands and artists.",
};

export default function AboutPage() {
  return (
    <main>
      <header>
        <h1>About SetlistApp</h1>
        <p>A local-first web app for building band setlists from a song catalog.</p>
      </header>
      <section className="panel">
        <h2>What it does</h2>
        <p>SetlistApp turns a catalog of songs into a performance-ready setlist. Add songs with key, tuning, and duration; configure the set; generate a setlist; then export it as text, CSV, JSON, or a shareable code.</p>
      </section>
      <section className="panel">
        <h2>How it works</h2>
        <ul>
          <li>Import a CSV song catalog (download the starter template if you need one).</li>
          <li>Mark songs active and tune keys, tunings, and durations.</li>
          <li>Set the set time, transition time, and generation weights, and mark required songs.</li>
          <li>Generate the setlist and edit order, duration, and content.</li>
          <li>Export, save, favorite, or share the setlist.</li>
        </ul>
      </section>
      <section className="panel">
        <h2>Features</h2>
        <ul>
          <li>Weighted setlist generation with original and mood weighting.</li>
          <li>Clustered ordering for smooth mood flow.</li>
          <li>Estimated set duration and transition time.</li>
          <li>Saved setlists, favorites, history, and backups.</li>
          <li>Share codes for sending a setlist to another performer.</li>
          <li>Performance timer and set-end countdown.</li>
          <li>Exports as TXT, CSV, JSON, and starter template.</li>
        </ul>
      </section>
      <section className="panel">
        <h2>Technology</h2>
        <p>The UI is built with Next.js and TypeScript; the setlist engine and file processing run in a Python FastAPI service with pandas; containers ship via Docker Compose. No account or database is required.</p>
      </section>
      <section className="panel">
        <h2>Self-hosting</h2>
        <p>The stack runs locally with Docker Compose and can be placed behind a reverse proxy for a custom domain. See the project README for the nginx configuration.</p>
      </section>
      <p><Link href="/">Back to the setlist builder</Link></p>
    </main>
  );
}
