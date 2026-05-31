import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PrijavaView from '@/views/PrijavaView.vue'
import NepoznatoView from '@/views/NepoznatoView.vue'
import AdminPocetnaView from '@/views/admin/AdminPocetnaView.vue'
import AdminKluboviView from '@/views/admin/AdminKluboviView.vue'
import KlubFormaView from '@/views/admin/KlubFormaView.vue'
import AdminKnjigeView from '@/views/admin/AdminKnjigeView.vue'
import KnjigaFormaView from '@/views/admin/KnjigaFormaView.vue'
import AdminClanstvaView from '@/views/admin/AdminClanstvaView.vue'
import AdminKorisniciView from '@/views/admin/AdminKorisniciView.vue'
import KorisnikFormaView from '@/views/admin/KorisnikFormaView.vue'
import ClanPocetnaView from '@/views/clan/ClanPocetnaView.vue'
import ClanKluboviView from '@/views/clan/ClanKluboviView.vue'
import ClanClanstvaView from '@/views/clan/ClanClanstvaView.vue'
import KnjigaKatalogView from '@/views/clan/KnjigaKatalogView.vue'
import MojeKnjigeView from '@/views/clan/MojeKnjigeView.vue'
import ClanProfilView from '@/views/clan/ClanProfilView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: () => {
        const auth = useAuthStore()
        if (!auth.isAuthenticated) return '/prijava'
        return auth.isAdmin ? '/admin/pocetna' : '/clan/pocetna'
      },
    },
    {
      path: '/prijava',
      component: PrijavaView,
      meta: { layout: 'gost', javno: true },
    },
    {
      path: '/admin',
      meta: { layout: 'aplikacija', uloga: 'admin' },
      children: [
        { path: 'pocetna', component: AdminPocetnaView },
        { path: 'klubovi', component: AdminKluboviView },
        { path: 'klubovi/novo', component: KlubFormaView },
        { path: 'klubovi/:id/uredi', component: KlubFormaView },
        { path: 'klubovi/:clubId/clanstva', component: AdminClanstvaView },
        { path: 'knjige', component: AdminKnjigeView },
        { path: 'knjige/novo', component: KnjigaFormaView },
        { path: 'knjige/:id/uredi', component: KnjigaFormaView },
        { path: 'korisnici', component: AdminKorisniciView },
        { path: 'korisnici/novo', component: KorisnikFormaView },
        { path: 'korisnici/:id/uredi', component: KorisnikFormaView },
      ],
    },
    {
      path: '/clan',
      meta: { layout: 'aplikacija', uloga: 'clan' },
      children: [
        { path: 'pocetna', component: ClanPocetnaView },
        { path: 'klubovi', component: ClanKluboviView },
        { path: 'clanstva', component: ClanClanstvaView },
        { path: 'knjige', component: KnjigaKatalogView },
        { path: 'moje-knjige', component: MojeKnjigeView },
        { path: 'profil', component: ClanProfilView },
      ],
    },
    {
      path: '/:catchAll(.*)*',
      component: NepoznatoView,
      meta: { layout: 'gost', javno: true },
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.javno) {
    if (auth.isAuthenticated) return auth.isAdmin ? '/admin/pocetna' : '/clan/pocetna'
    return true
  }

  if (!auth.isAuthenticated) return '/prijava'

  if (to.meta.uloga === 'admin' && !auth.isAdmin) return '/clan/pocetna'
  if (to.meta.uloga === 'clan' && !auth.isMember) return '/admin/pocetna'

  return true
})

export default router
