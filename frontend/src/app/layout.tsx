export const metadata = { title: "Email Bot Front (MVP)" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-br">
      <body style={{ fontFamily: "system-ui, sans-serif", padding: 20, maxWidth: 960, margin: "0 auto" }}>
        <h1 style={{ fontSize: 22, marginBottom: 16 }}>Email Bot – MVP</h1>
        {children}
      </body>
    </html>
  );
}
