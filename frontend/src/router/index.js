import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import SuperAdminDashboard from '../views/SuperAdminDashboard.vue'
import EstudianteDashboard from '../views/EstudianteDashboard.vue'
import CoordinadorLayout from '../views/coordinador/CoordinadorLayout.vue'
import CursosListView from '../views/coordinador/CursosListView.vue'
import CursoDetalleView from '../views/coordinador/CursoDetalleView.vue'
import InstitucionConfigView from '../views/coordinador/InstitucionConfigView.vue'
import AnalyticsGlobalView from '../views/coordinador/AnalyticsGlobalView.vue'
import CuentasView from '../views/coordinador/CuentasView.vue'
import ProfileView from '../views/coordinador/ProfileView.vue'

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
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
    
    // Check role-based access
    if (to.meta.role && authStore.user?.role !== to.meta.role) {
      // Redirect to appropriate dashboard based on user role
      if (authStore.user?.role === 'super_admin') {
        next('/super-admin')
      } else if (authStore.user?.role === 'coordinador') {
        next('/coordinador')
      } else if (authStore.user?.role === 'estudiante') {
        next('/estudiante')
      } else {
        next('/login')
      }
      return
    }
  }
  
  // Redirect authenticated users away from login
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next(authStore.dashboardRoute)
    return
  }
  
  next()
})

export default router