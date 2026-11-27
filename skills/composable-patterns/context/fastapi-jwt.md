
# FastAPI JWT composable pattern

```ts
// useApi.ts: attach Bearer token, refresh once on 401
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useApi() {
  const auth = useAuthStore();
  const loading = ref(false);
  const error = ref<Error | null>(null);

  async function send(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`/api${path}`, {
      ...init,
      headers: {
        Authorization: `Bearer ${auth.accessToken}`,
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  }

  async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
    loading.value = true;
    error.value = null;
    try {
      let res = await send(path, init);
      if (res.status === 401) {
        await auth.refresh();
        res = await send(path, init);
      }
      if (!res.ok) throw new Error(await res.text());
      return (await res.json()) as T;
    } catch (cause) {
      error.value = cause as Error;
      throw cause;
    } finally {
      loading.value = false;
    }
  }

  return { fetchApi, loading, error };
}
```
