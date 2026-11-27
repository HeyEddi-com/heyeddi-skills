
# Firebase client composable pattern

```ts
// useFirestoreCollection.ts: rules-aware reads
import { collection, onSnapshot, query, where } from "firebase/firestore";
import { ref, watchEffect } from "vue";
import { useFirebase } from "./useFirebase";

export function useFirestoreCollection<T>(name: string, ownerId: string) {
  const { db, user } = useFirebase();
  const items = ref<T[]>([]);
  const loading = ref(true);
  const error = ref<Error | null>(null);

  watchEffect((onCleanup) => {
    if (!user.value) return;
    try {
      const q = query(collection(db, name), where("ownerId", "==", ownerId));
      const unsubscribe = onSnapshot(
        q,
        (snap) => {
          items.value = snap.docs.map((d) => ({ id: d.id, ...d.data() }) as T);
          loading.value = false;
        },
        (cause) => {
          error.value = cause;
          loading.value = false;
        },
      );
      onCleanup(unsubscribe);
    } catch (cause) {
      error.value = cause as Error;
      loading.value = false;
    }
  });

  return { items, loading, error };
}
```
