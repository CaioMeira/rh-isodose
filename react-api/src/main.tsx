import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import Nifti from './Nifti.tsx'
import CT from './CT.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
 
    { <Nifti /> }
  </React.StrictMode>,
)

