# `src/lib/` – Core Logic & API Integration Pattern

This folder contains the core logic for API integration, state management, and type definitions for the HSYTP frontend. It is designed for scalability, maintainability, and clear separation of concerns.

## Integration Pattern

When adding a new API endpoint or feature, follow this pattern:

1. **Add to `requests.ts`:**
   - Define the raw API call (using Axios) in `requests.ts` under the relevant domain (e.g., `requests.portfolio.optimize`).
   - This file centralizes all HTTP requests and keeps API logic consistent.

2. **Define Types (if needed):**
   - If the endpoint returns new or complex data, add or update types in the `types/` folder (e.g., `types/portfolio.ts`).
   - This ensures type safety and better developer experience.

3. **Create/Update Repository:**
   - Add a repository in `repositories/` (e.g., `portfolio.repository.ts`) to encapsulate business logic, data transformation, and error handling for that domain.
   - Repositories call the raw requests and provide a clean interface for the rest of the app.

4. **Add Store (if needed):**
   - If the feature requires client-side state, add a store in `stores/` (e.g., `portfolio.store.ts`) using Zustand.
   - Stores manage UI state, caching, and reactivity.

5. **(Optional) Add/Update Model:**
   - If you need advanced data modeling or computed properties, add a model in `models/`.

## Folder Structure

- `api/` – Axios instance, circuit breaker, token manager, etc.
- `repositories/` – Business/data logic for each domain (portfolio, instrument, auth, ...)
- `stores/` – Zustand stores for state management
- `types/` – TypeScript types for API responses, requests, and domain models
- `utils/` – Utility functions and helpers

## Example: Adding a New Endpoint

1. **Add to `requests.ts`:**
   ```ts
   requests.myDomain = {
     myEndpoint: (params) => apiService.get('/api/v1/my-endpoint', { params }),
   };
   ```
2. **Add types:**
   ```ts
   // types/myDomain.ts
   export interface MyEndpointResponse { ... }
   ```
3. **Add repository:**
   ```ts
   // repositories/myDomain.repository.ts
   export const myDomainRepository = {
     myEndpoint: async (params) => {
       const result = await requests.myDomain.myEndpoint(params);
       // ...transform or validate result
       return result;
     },
   };
   ```
4. **Add store (if needed):**
   ```ts
   // stores/myDomain.store.ts
   import { create } from 'zustand';
   export const useMyDomainStore = create((set) => ({ ... }));
   ```

## Conventions
- Keep API logic out of UI components.
- Use repositories for all business/data logic.
- Use types everywhere for safety and clarity.
- Add JSDoc comments for public functions.

For more, see the codebase and existing examples in each subfolder.
