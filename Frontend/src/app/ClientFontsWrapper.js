"use client";

export default function ClientFontsWrapper({ children, geistSans, geistMono }) {
  return (
    <div className={`${geistSans.variable} ${geistMono.variable}`}>
      {children}
    </div>
  );
}
