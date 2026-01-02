# Performance Tips

## If the Application Freezes During Input

The application has been optimized to prevent freezing, but if you still experience issues:

### Reduce Update Frequency

The default update rate is 20Hz (50ms). If you experience freezing:

1. **Increase the sleep time** in `main.py`:
   - Find: `time.sleep(0.05)  # ~20Hz update rate`
   - Change to: `time.sleep(0.1)  # ~10Hz update rate` (slower but smoother)

2. **Increase UI update interval**:
   - Find: `self.ui_update_interval = 2`
   - Change to: `self.ui_update_interval = 4` (updates UI less frequently)

### Disable Expensive Features

If you don't need certain displays:

1. **Hide axis charts**: Close or minimize the "Axis Visual Display" section
2. **Reduce stats update**: The stats panel updates less frequently by default
3. **Limit mappings**: Too many servo mappings can slow things down

### System Performance

1. **Close other applications**: Free up CPU and memory
2. **Update graphics drivers**: Outdated drivers can cause UI freezing
3. **Check for background processes**: Antivirus or other software may interfere

### Arduino Communication

If Arduino communication is slow:

1. **Check baud rate**: Higher baud rates (115200) are faster
2. **Reduce servo count**: Fewer servos = less data to send
3. **Check USB cable**: Poor quality cables can cause delays

### Virtual Controller Performance

The virtual controller (on-screen wheel) is optimized and should not cause freezing. If it does:

1. **Reduce wheel widget size**: Smaller widgets render faster
2. **Disable auto-center**: Set auto-center speed to 0.0 if not needed

## Monitoring Performance

To see if the application is keeping up:

1. Watch the command confirmation rate in Arduino status
2. Check if servo movements are smooth or jerky
3. Monitor CPU usage in Task Manager

## If Freezing Persists

1. **Check Python version**: Use Python 3.8-3.11 for best performance
2. **Update tkinter**: Usually comes with Python, but check for updates
3. **Try different Python distribution**: Some distributions are optimized better

## Technical Details

The application uses:
- **Threading**: Input polling runs in a separate thread
- **Batched UI updates**: UI updates are batched to prevent queue buildup
- **Throttled updates**: UI updates are throttled to ~10Hz to prevent freezing
- **Error handling**: Errors are caught to prevent crashes

If you need maximum performance, consider:
- Using a faster computer
- Reducing the number of active displays
- Using a real game controller instead of virtual controller (if pygame works)

