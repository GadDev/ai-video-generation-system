import '../styles/globals.css';

export const metadata = {
  title: 'AI Video Generator',
  description: 'Generate anime video clips with AI',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
