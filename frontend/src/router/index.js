import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const Login = () => import('../views/Login.vue')
const SuperAdminDashboard = () => import('../views/SuperAdminDashboard.vue')
const EstudianteDashboard = () => import('../views/EstudianteDashboard.vue')
const CoordinadorLayout = () => import('../views/coordinador/CoordinadorLayout.vue')
const CursosListView = () => import('../views/coordinador/CursosListView.vue')
const CursoDetalleView = () => import('../views/coordinador/CursoDetalleView.vue')
const InstitucionConfigView = () => import('../views/coordinador/InstitucionConfigView.vue')
const AnalyticsGlobalView = () => import('../views/coordinador/AnalyticsGlobalView.vue')
const CuentasView = () => import('../views/coordinador/CuentasView.vue')
const ProfileView = () => import('../views/coordinador/ProfileView.vue')

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/super-admin',
    name: 'SuperAdminDashboard',
    component: SuperAdminDashboard,
    meta: { requiresAuth: true, role: 'super_admin' }
  },
  {
    path: '/coordinador',
    component: CoordinadorLayout,
    meta: { requiresAuth: true, role: 'coordinador' },
    children: [
      { path: '', redirect: '/coordinador/cursos' },
      { path: 'cursos', name: 'CoordinadorCursos', component: CursosListView },
      { path: 'cursos/:id', name: 'CoordinadorCursoDetalle', component: CursoDetalleView },
      { path: 'cuentas', name: 'CoordinadorCuentas', component: CuentasView },
      { path: 'institucion', name: 'CoordinadorInstitucion', component: InstitucionConfigView },
      { path: 'analytics', name: 'CoordinadorAnalytics', component: AnalyticsGlobalView },
      { path: 'perfil', name: 'CoordinadorPerfil', component: ProfileView }
    ]
  },
  {
    path: '/estudiante',
    name: 'EstudianteDashboard',
    component: EstudianteDashboard,
    meta: { requiresAuth: true, role: 'estudiante' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return '/login'
    }

    if (to.meta.role && authStore.user?.role !== to.meta.role) {
      return authStore.dashboardRoute
    }
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return authStore.dashboardRoute
  }
})

export default router