<template>
  <section class="bg-white rounded-xl shadow p-6 mb-8 max-w-4xl">
    <!-- Subject -->
    <div class="mb-4">
      <label class="block mb-1 font-medium">Subject</label>
      <select v-model="localSubject" class="w-48 px-3 py-2 border rounded">
        <option v-for="s in subjects" :key="s">{{ s }}</option>
      </select>
    </div>

    <!-- Lesson Content -->
    <div class="mb-4">
      <label class="block mb-1 font-medium">Lesson context</label>
      <textarea
        v-model="localText"
        rows="4"
        class="w-full px-3 py-2 border rounded"
        placeholder="Paste or insert…"
      ></textarea>
    </div>

    <!-- API Output -->
    <div class="mb-4">
      <label class="block mb-1 font-medium">API Outcome</label>
      <div class="w-full px-3 py-2 border rounded bg-gray-100 whitespace-pre-wrap">
        {{ localOutput }}
      </div>
    </div>

    <!-- Actions -->
    <div class="mb-4 flex gap-2">
      <button
        @click="emitGenerate"
        class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
      >
        Update Output
      </button>
    </div>

    <!-- Question Types -->
    
    <div class="mb-4">
      <label class="block mb-1 font-medium">Types & Numbers</label>
      <div class="flex flex-wrap gap-6">
        <label
          v-for="(cfg, type) in localTypes"
          :key="type"
          class="flex items-center gap-2"
        >
          <input type="checkbox" v-model="cfg.enabled" class="h-4 w-4" />
          {{ labelMap[type] }}
          <input
            type="number"
            v-model.number="cfg.num"
            class="w-20 px-1 py-1 border rounded text-center"
          />
        </label>
      </div>
    </div>
     <div>
     <button
        @click="emitGenerate"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Generate Questions
      </button>

     </div>
     
  </section>
</template>

<script>
export default {
  name: 'SettingsPanel',
  props: [
    'subjects',
    'selectedSubject',
    'textInput',
    'types',
    'labelMap',
    'apiOutput'
  ],
  emits: [
    'update:selectedSubject',
    'update:textInput',
    'update:types',
    'generate',
    'update:apiOutput'
  ],
  computed: {
    localSubject: {
      get() { return this.selectedSubject },
      set(v) { this.$emit('update:selectedSubject', v) }
    },
    localText: {
      get() { return this.textInput },
      set(v) { this.$emit('update:textInput', v) }
    },
    localTypes: {
      get() { return this.types },
      set(v) { this.$emit('update:types', v) }
    },
    localOutput() {
      return this.apiOutput
    }
  },
  methods: {
    emitGenerate() {
      this.$emit('generate')
    },
    emitUpdateOutput() {
      this.$emit('update:apiOutput', this.localText)
    }
  }
}
</script>