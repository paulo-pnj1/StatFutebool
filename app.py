'use client'; // ← importante para componentes interativos no Next.js App Router

import React, { useState } from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  TextField,
  Button,
  IconButton,
  Box,
  Grid,
  Paper,
  // outros componentes que você estiver usando...
} from '@mui/material';

import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  BarChart as AnalyticsIcon,          // ← corrigido: Analytics não existe, use BarChart
  Close as CloseIcon,
  LocationOn as LocationIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Cancel as CancelIcon,
  Phone as PhoneIcon,
  Timeline as TimelineIcon,
  Visibility as VisibilityIcon,
  Map as MapIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  LocationCity as LocationCityIcon,
  Refresh as RefreshIcon,
  Layers as LayersIcon,
  Notifications as NotificationsIcon,
  DateRange as DateRangeIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  MyLocation as MyLocationIcon,
  GetApp as GetAppIcon,
  SmartToy as SmartToyIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'; // ou AdapterDateFns, AdapterLuxon, etc.

// Tema customizado (opcional – ajuste conforme precisar)
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
  },
});

export default function MapaCasos() {
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  // ... outros estados que você tenha (ex: dados do mapa, filtros, etc.)

  const toggleFilters = () => setFiltersOpen(!filtersOpen);

  return (
    <ThemeProvider theme={theme}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Box sx={{ p: 3 }}>
          {/* Cabeçalho / Título */}
          <Typography variant="h4" gutterBottom>
            Mapa de Casos
          </Typography>

          {/* Barra de busca e filtros */}
          <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  placeholder="Buscar por nome, local ou ID..."
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                  }}
                />
              </Grid>

              <Grid item>
                <IconButton color="primary" onClick={toggleFilters}>
                  <FilterList />
                </IconButton>
              </Grid>

              <Grid item>
                <Button
                  variant="contained"
                  startIcon={<AnalyticsIcon />}
                  onClick={() => alert('Abrir dashboard de analytics')}
                >
                  Analytics
                </Button>
              </Grid>

              <Grid item>
                <IconButton color="primary">
                  <Refresh />
                </IconButton>
              </Grid>
            </Grid>
          </Paper>

          {/* Painel de Filtros (acordeão) */}
          <Accordion expanded={filtersOpen} onChange={toggleFilters}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Filtros Avançados</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <DatePicker
                    label="Data Inicial"
                    value={startDate}
                    onChange={(newValue) => setStartDate(newValue)}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <DatePicker
                    label="Data Final"
                    value={endDate}
                    onChange={(newValue) => setEndDate(newValue)}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </Grid>

                {/* Adicione aqui mais campos de filtro: status, tipo de caso, localização etc. */}
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Área principal do mapa */}
          <Paper elevation={3} sx={{ mt: 3, height: '70vh', position: 'relative' }}>
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'grey.100',
              }}
            >
              <Typography variant="h6" color="text.secondary">
                {/* Aqui vai o seu componente de mapa (ex: Leaflet, Google Maps, Mapbox etc.) */}
                Área do Mapa – Integre seu componente de mapa aqui
              </Typography>
            </Box>

            {/* Botões de controle do mapa (zoom, camadas, etc.) */}
            <Box sx={{ position: 'absolute', top: 16, right: 16, display: 'flex', flexDirection: 'column', gap: 1 }}>
              <IconButton color="primary" size="small">
                <ZoomIn />
              </IconButton>
              <IconButton color="primary" size="small">
                <ZoomOut />
              </IconButton>
              <IconButton color="primary" size="small">
                <MyLocation />
              </IconButton>
              <IconButton color="primary" size="small">
                <Layers />
              </IconButton>
            </Box>
          </Paper>
        </Box>
      </LocalizationProvider>
    </ThemeProvider>
  );
}
