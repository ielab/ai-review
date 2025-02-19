import { createRouter, createWebHistory } from 'vue-router'

// import { getAccountInfo } from '@/utils/auth'
// import { accountAuthStore } from './stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('./templates/Main.vue'),
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('./views/home/Home.vue'),
        },
        { path: 'jobs', name: 'jobs', component: () => import('./views/jobs/Jobs.vue') },
        {
          path: 'job/result/:id',
          name: 'result',
          component: () => import('./views/result/Result.vue'),
        },
        {
          path: 'job/create/:id',
          name: 'create',
          component: () => import('./views/jobCreate/jobCreate.vue'),
        },
        {
          path: 'preview',
          name: 'preview',
          component: () => import('./views/preview/Preview.vue'),
        },
        {
          path: 'upload',
          name: 'upload',
          component: () => import('./views/upload/Upload.vue'),
        },
        {
          path: 'collections',
          name: 'collections',
          component: () => import('./views/collections/Collections.vue'),
        },
        {
          path: 'login',
          name: 'login',
          component: () => import('./views/login/Login.vue'),
        },
        {
          path: 'sign-up',
          name: 'signUp',
          component: () => import('./views/signUp/SignUp.vue'),
        },
        {
          path: 'review',
          name: 'review',
          component: () => import('./views/review/Review.vue'),
        },
        {
          path: 'review2',
          name: 'review2',
          component: () => import('./views/review/Review.vue'),
        },
        {
          path: 'progress',
          name: 'progress',
          component: () => import('./views/progress/Progress.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'home' },
    },
  ],
})

// router.beforeEach(async (to, _, next) => {
//   // Check authentication
//   const accountInfo = await getAccountInfo()
//   if (accountInfo) Object.assign(accountAuthStore, accountInfo)

//   // For Page that not need to authenticate.
//   const PUBLIC_PATH_NAMES = ['home', 'signUp']
//   if (PUBLIC_PATH_NAMES.includes(to.name as string)) return next()

//   const destination = to.path === '/' ? undefined : to.fullPath
//   if (!accountInfo && !['login'].includes(to.name as string)) {
//     return next({ name: 'login', query: { next: destination } })
//   }
//   if (accountInfo && ['login'].includes(to.name as string)) {
//     return next({ name: 'home' })
//   }
//   next()
// })

export default router
