<template>
  <div class="contract-preview">
    <el-dialog
      v-model="dialogVisible"
      title="合同预览"
      width="80%"
      class="preview-dialog"
    >
      <div 
        v-loading="loading"
        class="preview-container"
      >
        <template v-if="fileType === 'pdf'">
          <iframe
            v-if="previewUrl"
            :src="previewUrl"
            class="preview-pdf"
          ></iframe>
        </template>
        <template v-else-if="['jpg', 'jpeg', 'png'].includes(fileType)">
          <img
            v-if="previewUrl"
            :src="previewUrl"
            class="preview-image"
            alt="预览图片"
          >
        </template>
        <div v-else class="preview-unsupported">
          该文件类型不支持预览
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  previewUrl: string
  fileType: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const dialogVisible = ref(props.visible)
const loading = ref(false)

// 监听 visible 属性变化
watch(() => props.visible, (newValue) => {
  dialogVisible.value = newValue
})

// 监听 dialogVisible 变化
watch(() => dialogVisible.value, (newValue) => {
  emit('update:visible', newValue)
})
</script>

<style scoped>
.contract-preview {
  .preview-dialog :deep(.el-dialog__body) {
    padding: 0;
  }

  .preview-container {
    height: 600px;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #f5f7fa;
  }

  .preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  .preview-pdf {
    width: 100%;
    height: 100%;
    border: none;
  }

  .preview-unsupported {
    text-align: center;
    color: #909399;
    padding: 20px;
  }
}
</style> 