<template>
  <div class="card">
    <img class="card-image" :src="record.image" alt="Violation Image" />
    <ul class="card-info">
      <li><strong>Type:</strong> {{ record.type }}</li>
      <li><strong>Timestamp:</strong> {{ record.timestamp }}</li>
      <li><strong>License Plate:</strong> {{ record.plate }}</li>
      <li><strong>Location:</strong> {{ record.location }}</li>
    </ul>
  </div>
</template>

<script setup>
// 使用 defineProps 并直接引用 record，不定义 props 变量
defineProps({
  record: {
    type: Object,
    required: true,
  }
})
</script>

<style scoped>
.card {
  display: flex;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
  background-color: white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.card-image {
  width: 240px;
  height: 320px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 16px;
  background-color: #eee;
}

.card-info {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 14px;
}

.card-info li {
  margin-bottom: 8px;
}
</style>
