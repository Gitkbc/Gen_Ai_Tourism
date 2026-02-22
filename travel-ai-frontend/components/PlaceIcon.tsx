"use client";

type PlaceKind =
  | "temple"
  | "fort"
  | "museum"
  | "garden"
  | "market"
  | "food"
  | "nature"
  | "landmark";

interface PlaceIconProps {
  placeName: string;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

function getPlaceKind(placeName: string): PlaceKind {
  const name = placeName.toLowerCase();

  if (/temple|ganapati|ganpati|devi|mandir|dargah|church|mosque/.test(name)) {
    return "temple";
  }
  if (/fort|wada|mahal|palace|qila|citadel/.test(name)) {
    return "fort";
  }
  if (/museum|gallery|archive|planetarium/.test(name)) {
    return "museum";
  }
  if (/garden|park|lake|hill|river|beach/.test(name)) {
    return "garden";
  }
  if (/market|bazaar|mall|street|city|shopping|baug/.test(name)) {
    return "market";
  }
  if (/cafe|restaurant|food|eatery|kitchen/.test(name)) {
    return "food";
  }
  if (/sanctuary|forest|zoo|trail|valley/.test(name)) {
    return "nature";
  }
  return "landmark";
}

const STYLE_MAP: Record<
  PlaceKind,
  { wrapper: string; label: string; icon: string; title: string }
> = {
  temple: {
    wrapper: "from-amber-400/20 to-orange-500/10 border-amber-300/30",
    label: "text-amber-200",
    icon: "text-amber-100",
    title: "Temple",
  },
  fort: {
    wrapper: "from-stone-400/20 to-slate-500/10 border-stone-300/30",
    label: "text-stone-200",
    icon: "text-stone-100",
    title: "Heritage",
  },
  museum: {
    wrapper: "from-violet-400/20 to-indigo-500/10 border-violet-300/30",
    label: "text-violet-200",
    icon: "text-violet-100",
    title: "Museum",
  },
  garden: {
    wrapper: "from-emerald-400/20 to-green-500/10 border-emerald-300/30",
    label: "text-emerald-200",
    icon: "text-emerald-100",
    title: "Nature",
  },
  market: {
    wrapper: "from-cyan-400/20 to-blue-500/10 border-cyan-300/30",
    label: "text-cyan-200",
    icon: "text-cyan-100",
    title: "Market",
  },
  food: {
    wrapper: "from-rose-400/20 to-red-500/10 border-rose-300/30",
    label: "text-rose-200",
    icon: "text-rose-100",
    title: "Food",
  },
  nature: {
    wrapper: "from-lime-400/20 to-emerald-500/10 border-lime-300/30",
    label: "text-lime-200",
    icon: "text-lime-100",
    title: "Outdoors",
  },
  landmark: {
    wrapper: "from-sky-400/20 to-blue-500/10 border-sky-300/30",
    label: "text-sky-200",
    icon: "text-sky-100",
    title: "Landmark",
  },
};

function LandmarkGlyph({ kind }: { kind: PlaceKind }) {
  if (kind === "temple") {
    return (
      <svg viewBox="0 0 24 24" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 20h16M6 20v-8l6-6 6 6v8M10 14h4" />
      </svg>
    );
  }

  if (kind === "fort") {
    return (
      <svg viewBox="0 0 24 24" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 20V7h3v3h4V7h2v3h4V7h3v13" />
        <path d="M10 20v-5h4v5" />
      </svg>
    );
  }

  if (kind === "museum") {
    return (
      <svg viewBox="0 0 24 24" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3 9h18M4 20h16M6 9V6l6-3 6 3v3M8 20v-8M12 20v-8M16 20v-8" />
      </svg>
    );
  }

  if (kind === "garden" || kind === "nature") {
    return (
      <svg viewBox="0 0 24 24" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M12 20v-8M12 12c0-3 2-5 5-5 0 3-2 5-5 5ZM12 14c-3 0-5-2-5-5 3 0 5 2 5 5Z" />
      </svg>
    );
  }

  if (kind === "food") {
    return (
      <svg viewBox="0 0 24 24" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M6 4v8M9 4v8M6 8h3M16 4v16M13 9h6" />
      </svg>
    );
  }

  if (kind === "market") {
    return (
      <svg viewBox="0 0 24 24" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 8h16l-1.5 4.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5L4 8Zm2 6v6h12v-6" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 21s7-4.5 7-10a7 7 0 1 0-14 0c0 5.5 7 10 7 10Z" />
      <path d="M12 14a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" />
    </svg>
  );
}

export default function PlaceIcon({ placeName, size = "md", showLabel = true }: PlaceIconProps) {
  const kind = getPlaceKind(placeName);
  const style = STYLE_MAP[kind];

  const sizeClass =
    size === "sm"
      ? "h-10 w-10"
      : size === "lg"
        ? "h-20 w-20"
        : "h-14 w-14";

  return (
    <div className={`rounded-xl border bg-gradient-to-br ${style.wrapper} p-4`}>
      <div className="flex items-center gap-3">
        <div className={`${sizeClass} rounded-xl border border-white/15 bg-black/35 p-2 ${style.icon}`}>
          <LandmarkGlyph kind={kind} />
        </div>
        {showLabel ? (
          <div>
            <p className={`text-xs uppercase tracking-[0.18em] ${style.label}`}>{style.title}</p>
            <p className="mt-1 text-sm font-medium text-white">{placeName}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
