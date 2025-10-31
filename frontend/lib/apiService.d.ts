export const uploadFile: (file: File) => Promise<{ message: string; file_path: string }>;
export const analyzeData: (filePath: string) => Promise<any>;
