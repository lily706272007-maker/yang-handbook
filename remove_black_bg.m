#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSString *inputPath = @"/Users/yangyongzhu/.gemini/antigravity/brain/b58ba25a-e9f5-48ce-a86c-daf46a4f945e/.user_uploaded/media_1787810826335.jpg";
        NSString *outputPath = @"/Users/yangyongzhu/.gemini/antigravity/scratch/yang-pwa/icons/tanuki.png";
        
        NSImage *srcImage = [[NSImage alloc] initWithContentsOfFile:inputPath];
        if (!srcImage) {
            NSLog(@"Failed to load image");
            return 1;
        }
        
        NSBitmapImageRep *rep = [[NSBitmapImageRep alloc] initWithData:[srcImage TIFFRepresentation]];
        NSInteger width = [rep pixelsWide];
        NSInteger height = [rep pixelsHigh];
        
        // Create 32-bit RGBA bitmap
        NSBitmapImageRep *outRep = [[NSBitmapImageRep alloc] 
            initWithBitmapDataPlanes:NULL
            pixelsWide:width
            pixelsHigh:height
            bitsPerSample:8
            samplesPerPixel:4
            hasAlpha:YES
            isPlanar:NO
            colorSpaceName:NSCalibratedRGBColorSpace
            bytesPerRow:width * 4
            bitsPerPixel:32];
            
        unsigned char *srcData = [rep bitmapData];
        NSInteger srcBPP = [rep bitsPerPixel] / 8;
        NSInteger srcBPR = [rep bytesPerRow];
        unsigned char *outData = [outRep bitmapData];
        
        // Flood fill / thresholding from corners or pure black keying
        // Since the background is pure black (#000000 or near black), we key out near-black pixels
        for (NSInteger y = 0; y < height; y++) {
            for (NSInteger x = 0; x < width; x++) {
                unsigned char *sp = srcData + y * srcBPR + x * srcBPP;
                unsigned char *dp = outData + (y * width + x) * 4;
                
                unsigned char r = sp[0];
                unsigned char g = sp[1];
                unsigned char b = sp[2];
                
                int brightness = (int)r + (int)g + (int)b;
                
                if (brightness < 18) {
                    // Pure background
                    dp[0] = 0;
                    dp[1] = 0;
                    dp[2] = 0;
                    dp[3] = 0;
                } else if (brightness < 45) {
                    // Smooth antialiased edge
                    float alpha = (float)(brightness - 18) / 27.0f;
                    dp[0] = r;
                    dp[1] = g;
                    dp[2] = b;
                    dp[3] = (unsigned char)(alpha * 255);
                } else {
                    dp[0] = r;
                    dp[1] = g;
                    dp[2] = b;
                    dp[3] = 255;
                }
            }
        }
        
        // Flood fill from borders to only remove connected background so that black eyes/pupils inside the character are NOT removed!
        // Let's do a flood fill mask from (0,0)
        int *visited = calloc(width * height, sizeof(int));
        int *queueX = malloc(width * height * sizeof(int));
        int *queueY = malloc(width * height * sizeof(int));
        int head = 0, tail = 0;
        
        // Push all border pixels that are dark
        for (NSInteger x = 0; x < width; x++) {
            queueX[tail] = (int)x; queueY[tail] = 0; visited[0 * width + x] = 1; tail++;
            queueX[tail] = (int)x; queueY[tail] = (int)(height - 1); visited[(height - 1) * width + x] = 1; tail++;
        }
        for (NSInteger y = 0; y < height; y++) {
            if (!visited[y * width + 0]) {
                queueX[tail] = 0; queueY[tail] = (int)y; visited[y * width + 0] = 1; tail++;
            }
            if (!visited[y * width + (width - 1)]) {
                queueX[tail] = (int)(width - 1); queueY[tail] = (int)y; visited[y * width + (width - 1)] = 1; tail++;
            }
        }
        
        int dx[] = {0, 0, 1, -1};
        int dy[] = {1, -1, 0, 0};
        
        while (head < tail) {
            int cx = queueX[head];
            int cy = queueY[head];
            head++;
            
            unsigned char *sp = srcData + cy * srcBPR + cx * srcBPP;
            int b = (int)sp[0] + (int)sp[1] + (int)sp[2];
            
            if (b < 60) { // Dark background connected component
                for (int d = 0; d < 4; d++) {
                    int nx = cx + dx[d];
                    int ny = cy + dy[d];
                    if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                        if (!visited[ny * width + nx]) {
                            visited[ny * width + nx] = 1;
                            queueX[tail] = nx;
                            queueY[tail] = ny;
                            tail++;
                        }
                    }
                }
            }
        }
        
        // Reset non-background pixels: if not connected to border black, restore alpha to 255 (protects dark eyes!)
        for (NSInteger y = 0; y < height; y++) {
            for (NSInteger x = 0; x < width; x++) {
                unsigned char *sp = srcData + y * srcBPR + x * srcBPP;
                unsigned char *dp = outData + (y * width + x) * 4;
                if (!visited[y * width + x]) {
                    // Interior of character (even if black, like eyes/nose)
                    dp[0] = sp[0];
                    dp[1] = sp[1];
                    dp[2] = sp[2];
                    dp[3] = 255;
                }
            }
        }
        
        free(visited);
        free(queueX);
        free(queueY);
        
        NSData *pngData = [outRep representationUsingType:NSBitmapImageFileTypePNG properties:@{}];
        [pngData writeToFile:outputPath atomically:YES];
        NSLog(@"Saved transparent tanuki PNG to %@", outputPath);
    }
    return 0;
}
